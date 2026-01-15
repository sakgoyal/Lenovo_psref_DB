use polars::prelude::*;
use regex::Regex;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::sync::LazyLock;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

static REGEX_REPLACEMENTS: LazyLock<Vec<(Regex, &'static str)>> = LazyLock::new(|| {
    vec![
        (Regex::new(r"(\^\|\^)?Various docking.*?</u></a>").unwrap(), "Various"),
        (Regex::new(r"Non-WWAN").unwrap(), ""),
        (Regex::new(r"NVIDIA (GeForce )?").unwrap(), ""),
        (Regex::new(r"Boost Clock ").unwrap(), ""),
        (Regex::new(r"TGP ").unwrap(), ""),
        (Regex::new(r"None").unwrap(), ""),
        (Regex::new(r"RoHS compliant").unwrap(), "RoHS"),
        (Regex::new(r"military test passed").unwrap(), ""),
        (Regex::new(r"Integrated AMD Radeon ").unwrap(), "AMD Radeon "),
        (Regex::new(r"Memory soldered to systemboard, no slots").unwrap(), "No Slots"),
        (Regex::new(r"microSD Card Reader").unwrap(), "microSD"),
        (Regex::new(r"TPM 2.0 Enabled").unwrap(), "TPM 2.0"),
        (Regex::new(r"1x Ethernet \(RJ-45\)").unwrap(), "Ethernet"),
        (Regex::new(r"100/1000M \(RJ-45\)").unwrap(), "1GbE"),
        (Regex::new(r"2.5GbE \(RJ-45\)").unwrap(), "2.5GbE"),
        (Regex::new(r"No [oO]nboard Ethernet").unwrap(), ""),
        (Regex::new(r"Pen Not Supported").unwrap(), ""),
        (Regex::new(r"No support").unwrap(), ""),
        (Regex::new(r"No card reader").unwrap(), ""),
        (Regex::new(r"Non-AI PC").unwrap(), ""),
        (Regex::new(r"No smart card reader").unwrap(), ""),
        (Regex::new(r"High Definition \(HD\) Audio, ").unwrap(), ""),
        (Regex::new(r"No color calibration").unwrap(), ""),
        (Regex::new(r"Kensington Nano Security Slot, 2.5 x 6 mm").unwrap(), "Kensington Nano"),
        (Regex::new(r"No physical locks").unwrap(), ""),
        (Regex::new(r"Headphone / microphone combo jack \(3.5mm\)").unwrap(), "3.5mm Combo Jack"),
        (Regex::new(r"\^\|\^").unwrap(), " | "),
        (Regex::new(r"IR camera for Windows Hello \(facial recognition\)").unwrap(), "Windows Hello IR Camera"),
        (Regex::new(r"\u{00a0}").unwrap(), " "),
    ]
});

#[derive(Debug, Deserialize)]
struct ApiResponse<T> {
    data: Option<T>,
}

#[derive(Debug, Deserialize)]
struct ProductIDs {
    id: String,
    #[serde(rename = "type")]
    type_: Option<String>,
    subcollection: Option<Vec<ProductIDs>>,
}

#[derive(Debug, Deserialize)]
struct ShowModel {
    cols: Vec<String>,
    rows: Vec<Vec<String>>,
}

fn extract_product_ids(items: &[ProductIDs]) -> Vec<String> {
    let mut ids = Vec::new();
    for item in items {
        if item.type_.as_deref() == Some("product") {
            ids.push(item.id.clone());
        }
        if let Some(ref sub) = item.subcollection {
            ids.extend(extract_product_ids(sub));
        }
    }
    ids
}

fn apply_replacements(text: &str) -> String {
    let mut result = text.to_string();
    for (pattern, replacement) in REGEX_REPLACEMENTS.iter() {
        result = pattern.replace_all(&result, *replacement).to_string();
    }
    result.replace(['\r', '\n'], " ").trim().to_string()
}

fn fetch_product_df(client: &reqwest::blocking::Client, product_id: &str) -> Result<DataFrame> {
    print!("{}: Downloading...", product_id);
    std::io::stdout().flush()?;

    let url = format!(
        "https://psref.lenovo.com/api/search/DefinitionFilterAndSearch/ShowModel?pageindex=1&pagesize=300000&product_key={}",
        product_id
    );

    let response: ApiResponse<ShowModel> = client
        .get(&url)
        .send()
        .map_err(|e| format!("Failed to fetch data: {}", e))?
        .json()
        .map_err(|e| format!("Failed to parse JSON: {}", e))?;

    let data = response.data.ok_or("No data found")?;

    print!("Processing...");
    std::io::stdout().flush()?;

    let mut cols_data: Vec<Vec<String>> = vec![Vec::with_capacity(data.rows.len()); data.cols.len()];

    for row in data.rows {
        for (i, cell) in row.into_iter().enumerate() {
            if i < cols_data.len() {
                cols_data[i].push(apply_replacements(&cell));
            }
        }
    }

    // Convert Series to Columns
    let columns: Vec<Column> = data.cols.into_iter()
        .zip(cols_data)
        .map(|(name, vals)| Series::new(name.into(), vals).into())
        .collect();

    println!("Done.");
    Ok(DataFrame::new(columns)?)
}

const OMIT_COLUMNS: &[&str] = &[
    "EAN / UPC / JAN", "Model", "Machine Type", "TopSeller", "Monitor Cable",
    "Controls", "Others", "ISV Certifications", "Base Warranty",
    "Other Certifications", "Included Upgrade", "End of Support", "Announce Date",
];

const FILTER_OMIT_COLUMNS: &[&str] = &[
    "Region", "Screen-to-Body Ratio", "Optical", "Docking", "Included Upgrade",
    "Announce Date", "Standard Ports", "Operating System", "Dimensions (WxDxH)",
    "Product", "End of Support",
];

fn get_distinct_values(df: &DataFrame) -> Result<HashMap<String, Vec<String>>> {
    let omit_set: HashSet<&str> = OMIT_COLUMNS.iter().copied().collect();
    let mut result: HashMap<String, Vec<String>> = HashMap::new();

    for col_name in df.get_column_names() {
        if omit_set.contains(col_name.as_str()) {
            continue;
        }

        let unique = df.column(col_name)?.unique()?.cast(&DataType::String)?;
        let mut values: Vec<String> = unique
            .str()?
            .into_iter()
            .flatten()
            .map(|s| s.to_string())
            .filter(|s| !s.is_empty() && s.to_lowercase() != "nan")
            .collect();
        values.sort();
        result.insert(col_name.to_string(), values);
    }

    Ok(result)
}

fn create_filter_values_parquet(distinct_values: &HashMap<String, Vec<String>>) -> Result<()> {
    let (col_names, options): (Vec<String>, Vec<String>) = distinct_values.iter()
        .map(|(k, v)| (k.clone(), serde_json::to_string(v).unwrap_or_default()))
        .unzip();

    // Convert Series to Columns
    let mut df = DataFrame::new(vec![
        Series::new("column_name".into(), col_names).into(),
        Series::new("options".into(), options).into(),
    ])?;

    let file = File::create("database/filter_values.parquet")?;
    ParquetWriter::new(file).finish(&mut df)?;

    println!("Saved database/filter_values.parquet");
    Ok(())
}

fn generate_typescript_filters(distinct_values: &HashMap<String, Vec<String>>) -> Result<()> {
    let filter_omit_full: HashSet<&str> = OMIT_COLUMNS.iter()
        .chain(FILTER_OMIT_COLUMNS.iter())
        .copied()
        .collect();

    let filter_dict: HashMap<&str, &Vec<String>> = distinct_values.iter()
        .filter(|(k, _)| !filter_omit_full.contains(k.as_str()))
        .map(|(k, v)| (k.as_str(), v))
        .collect();

    let mut file = File::create("./data.ts")?;
    writeln!(file, "export const filters = {}", serde_json::to_string_pretty(&filter_dict)?)?;

    println!("Saved ./data.ts");
    Ok(())
}

fn main() -> Result<()> {
    let client = reqwest::blocking::Client::builder()
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
        .build()?;

    println!("Fetching product IDs...");
    let response: ApiResponse<Vec<ProductIDs>> = client
        .get("https://psref.lenovo.com/api/home/Menu/info")
        .send()?
        .json()?;

    let product_ids = response.data
        .as_ref()
        .and_then(|d| d.first())
        .and_then(|f| f.subcollection.as_ref())
        .map(|s| extract_product_ids(s))
        .unwrap_or_default();

    println!("Fetched {} product IDs.", product_ids.len());

    let limit: Option<usize> = std::env::args().nth(1).and_then(|s| s.parse().ok());
    let mut dfs: Vec<DataFrame> = Vec::new();

    for (i, product_id) in product_ids.iter().enumerate() {
        if let Some(max) = limit {
            if i >= max { break; }
        }
        match fetch_product_df(&client, product_id) {
            Ok(df) => dfs.push(df),
            Err(e) => eprintln!("Error processing {}: {}", product_id, e),
        }
    }

    if dfs.is_empty() {
        return Err("No data fetched.".into());
    }

    println!("Merging DataFrames...");
    let mut combined = polars::functions::concat_df_diagonal(&dfs)?;

    fs::create_dir_all("database")?;
    let file = File::create("database/products.parquet")?;
    ParquetWriter::new(file).finish(&mut combined)?;
    println!("Saved database/products.parquet with {} rows.", combined.height());

    println!("Extracting distinct values...");
    let distinct_values = get_distinct_values(&combined)?;

    println!("Creating filter values parquet...");
    create_filter_values_parquet(&distinct_values)?;

    println!("Generating TypeScript filters...");
    generate_typescript_filters(&distinct_values)?;

    println!("Done!");
    Ok(())
}
