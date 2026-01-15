use polars::prelude::*;
use regex::Regex;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
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

fn escape_csv(val: &str) -> String {
    let s = val.replace('"', "\"\"").replace(['\r', '\n'], " ");
    if s.contains([',', '"', '\n', '\r']) {
        format!("\"{}\"", s)
    } else {
        s
    }
}

fn apply_replacements(text: &str) -> String {
    let mut result = text.to_string();
    for (pattern, replacement) in REGEX_REPLACEMENTS.iter() {
        result = pattern.replace_all(&result, *replacement).to_string();
    }
    result
}

fn download_data(client: &reqwest::blocking::Client, product_id: &str) -> Result<()> {
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

    print!("Processing...");
    std::io::stdout().flush()?;

    let data = response.data.ok_or("No data found")?;

    let mut csv_lines = Vec::with_capacity(data.rows.len() + 1);
    csv_lines.push(data.cols.iter().map(|c| escape_csv(c)).collect::<Vec<_>>().join(","));

    for row in &data.rows {
        csv_lines.push(row.iter().map(|c| escape_csv(c)).collect::<Vec<_>>().join(","));
    }

    let text = csv_lines.join("\n");
    let text = apply_replacements(&text);

    fs::write(format!("out/{}.csv", product_id), text)?;

    println!("Done.");
    Ok(())
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

fn merge_csvs_to_parquet() -> Result<DataFrame> {
    let out_path = Path::new("out");
    let mut dfs: Vec<DataFrame> = Vec::new();

    for entry in fs::read_dir(out_path)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().is_some_and(|e| e == "csv") {
            let df = CsvReadOptions::default()
                .with_infer_schema_length(Some(0))
                .with_has_header(true)
                .try_into_reader_with_file_path(Some(path.clone()))?
                .finish()?;
            dfs.push(df);
        }
    }

    if dfs.is_empty() {
        return Err("No CSV files found in out/".into());
    }

    // Collect all unique column names and sort them for consistent ordering
    let mut all_columns: Vec<String> = dfs
        .iter()
        .flat_map(|df| df.get_column_names_owned())
        .collect::<HashSet<_>>()
        .into_iter()
        .map(|s| s.to_string())
        .collect();
    all_columns.sort();

    // Align all DataFrames to have the same columns in the same order
    let aligned_dfs: Vec<DataFrame> = dfs
        .into_iter()
        .map(|df| {
            // Check which columns exist
            let existing_cols: HashSet<String> = df
                .get_column_names()
                .into_iter()
                .map(|s| s.to_string())
                .collect();

            let mut lf = df.lazy();

            // Add missing columns as null
            for col_name in &all_columns {
                if !existing_cols.contains(col_name) {
                    lf = lf.with_column(lit(NULL).cast(DataType::String).alias(col_name.as_str()));
                }
            }

            // Cast all columns to string
            for col_name in &all_columns {
                lf = lf.with_column(col(col_name.as_str()).cast(DataType::String));
            }

            // Select columns in consistent order
            let col_exprs: Vec<Expr> = all_columns.iter().map(|c| col(c.as_str())).collect();
            lf = lf.select(col_exprs);

            lf.collect().unwrap()
        })
        .collect();

    // Concatenate all DataFrames
    let combined = concat(
        aligned_dfs.iter().map(|df| df.clone().lazy()).collect::<Vec<_>>(),
        UnionArgs::default(),
    )?
    .collect()?;

    fs::create_dir_all("database")?;
    let file = File::create("database/products.parquet")?;
    ParquetWriter::new(file)
        .with_compression(ParquetCompression::Uncompressed)
        .finish(&mut combined.clone())?;

    println!("Saved database/products.parquet with {} rows.", combined.height());
    Ok(combined)
}

fn get_distinct_values(df: &DataFrame) -> Result<HashMap<String, Vec<String>>> {
    let omit_set: HashSet<&str> = OMIT_COLUMNS.iter().copied().collect();
    let mut result: HashMap<String, Vec<String>> = HashMap::new();

    for col_name in df.get_column_names() {
        if omit_set.contains(col_name.as_str()) {
            continue;
        }

        let series = df.column(col_name)?;
        let unique = series.unique()?.cast(&DataType::String)?;
        let mut values: Vec<String> = unique
            .str()?
            .into_iter()
            .filter_map(|opt| opt.map(|s| s.to_string()))
            .filter(|s| !s.is_empty() && s.to_lowercase() != "nan")
            .collect();
        values.sort();
        result.insert(col_name.to_string(), values);
    }

    Ok(result)
}

fn create_filter_values_parquet(distinct_values: &HashMap<String, Vec<String>>) -> Result<()> {
    let mut col_names: Vec<String> = Vec::new();
    let mut options: Vec<String> = Vec::new();

    for (col, vals) in distinct_values {
        col_names.push(col.clone());
        options.push(serde_json::to_string(vals)?);
    }

    let df = DataFrame::new(vec![
        Column::new("column_name".into(), col_names),
        Column::new("options".into(), options),
    ])?;

    let file = File::create("database/filter_values.parquet")?;
    ParquetWriter::new(file)
        .with_compression(ParquetCompression::Uncompressed)
        .finish(&mut df.clone())?;

    println!("Saved database/filter_values.parquet");
    Ok(())
}

fn generate_typescript_filters(distinct_values: &HashMap<String, Vec<String>>) -> Result<()> {
    let filter_omit_full: HashSet<&str> = OMIT_COLUMNS
        .iter()
        .chain(FILTER_OMIT_COLUMNS.iter())
        .copied()
        .collect();

    let mut filter_dict: HashMap<&str, &Vec<String>> = HashMap::new();
    for (col, vals) in distinct_values {
        if !filter_omit_full.contains(col.as_str()) {
            filter_dict.insert(col.as_str(), vals);
        }
    }

    fs::create_dir_all("finder/src/routes")?;
    let mut file = File::create("finder/src/routes/data.ts")?;
    writeln!(file, "export const filters = {}", serde_json::to_string_pretty(&filter_dict)?)?;

    println!("Saved finder/src/routes/data.ts");
    Ok(())
}

fn main() -> Result<()> {
    fs::create_dir_all("out")?;

    let client = reqwest::blocking::Client::builder()
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
        .build()?;

    println!("Fetching product IDs...");

    let response: ApiResponse<Vec<ProductIDs>> = client
        .get("https://psref.lenovo.com/api/home/Menu/info")
        .send()
        .map_err(|e| format!("Failed to fetch menu: {}", e))?
        .json()
        .map_err(|e| format!("Failed to parse menu JSON: {}", e))?;

    let menu_data = response.data.ok_or("No menu data")?;

    let product_ids = if let Some(first) = menu_data.first() {
        if let Some(ref sub) = first.subcollection {
            extract_product_ids(sub)
        } else {
            Vec::new()
        }
    } else {
        Vec::new()
    };

    println!("Fetched {} product IDs.", product_ids.len());

    let limit: Option<usize> = std::env::args().nth(1).and_then(|s| s.parse().ok());

    for (i, product_id) in product_ids.iter().enumerate() {
        if let Some(max) = limit {
            if i >= max {
                break;
            }
        }
        if let Err(e) = download_data(&client, product_id) {
            eprintln!("Error processing {}: {}", product_id, e);
        }
    }

    println!("Merging CSVs to Parquet...");
    let combined_df = merge_csvs_to_parquet()?;

    println!("Extracting distinct values...");
    let distinct_values = get_distinct_values(&combined_df)?;

    println!("Creating filter values parquet...");
    create_filter_values_parquet(&distinct_values)?;

    println!("Generating TypeScript filters...");
    generate_typescript_filters(&distinct_values)?;

    println!("Closing Client...");
    drop(client);

    println!("Done!");
    Ok(())
}
