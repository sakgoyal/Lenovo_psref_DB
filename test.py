import duckdb
con = duckdb.connect()

# Read CSV and write to Parquet
con.execute(f"""
    COPY (SELECT * FROM read_csv_auto('out/zzz.csv'))
    TO 'out/duckdb.pq' (FORMAT PARQUET)
""").commit()

con.close()
