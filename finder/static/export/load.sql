COPY filter_values FROM 'finder/static/export/filter_values.parquet' (FORMAT 'parquet');
COPY products FROM 'finder/static/export/products.parquet' (FORMAT 'parquet');
