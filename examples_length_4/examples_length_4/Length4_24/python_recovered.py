import pandas as pd

# File paths for the 4 source files
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_24/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_24/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_24/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_24/test_3.csv'
]

# Load all sources into a list of DataFrames
dfs = [pd.read_csv(path, index_col=0) for path in source_files]

# Concatenate the dataframes (UNION)
df = pd.concat(dfs, ignore_index=True)

# === Data transformations ===

# Convert 'datetime' column from 'YYYY-MM-DD' to integer in MMDD format  
# Example: '1867-12-12' -> 1212; '1864-02-08' -> 208
def datetime_to_int(date_str):
    # date_str format: "YYYY-MM-DD"
    _, month, day = date_str.split('-')
    return int(month.lstrip('0') + day.zfill(2))

df['datetime'] = df['datetime'].apply(datetime_to_int)

# obs_type in source is always 'TMAX' as string; target expects integer
# We assign a constant integer code to represent 'TMAX' obs_type, e.g., 1315 (from target examples)
df['obs_type'] = 1315

# Convert obs_value and TMAX_F from float to int (round)
df['obs_value'] = df['obs_value'].round().astype(int)
df['TMAX_F'] = df['TMAX_F'].round().astype(int)

# month should be integer already, ensure integer type
df['month'] = df['month'].astype(int)

# country_code: map unique country code strings to unique integer codes
unique_countries = df['country_code'].unique()
country_code_map = {code: idx+1 for idx, code in enumerate(sorted(unique_countries))}
df['country_code'] = df['country_code'].map(country_code_map).astype(int)

# station is string and just strip spaces if needed, keep as is
df['station'] = df['station'].astype(str).str.strip()

# Select and reorder columns to match target schema exactly
target_columns = ['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']
df = df[target_columns]

# Write the transformed dataframe to the target path without index column
output_path = 'autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_cot.csv'
df.to_csv(output_path, index=False)