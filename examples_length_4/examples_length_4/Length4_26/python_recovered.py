import pandas as pd

# Paths to source CSV files
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_26/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_26/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_26/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_26/test_3.csv',
]

# List to hold dataframes
df_list = []

# Read each source CSV file with index_col=0 (ignore first numerical index column)
for file_path in source_files:
    df = pd.read_csv(file_path, index_col=0)
    df_list.append(df)

# Concatenate all source tables into one DataFrame
df_all = pd.concat(df_list, ignore_index=True)

# Convert 'datetime' from 'YYYY-MM-DD' string to integer YYYYMMDD
# Example: '1866-01-07' -> 18660107
df_all['datetime'] = pd.to_datetime(df_all['datetime'], format='%Y-%m-%d', errors='coerce')
df_all = df_all[df_all['datetime'].notna()]  # Drop rows with invalid datetime (if any)
df_all['datetime'] = df_all['datetime'].dt.strftime('%Y%m%d').astype(int)

# Encode categorical columns to integer codes:
# 'station', 'obs_type', 'country_code'
# Using categorical dtype and .cat.codes will assign consistent integer codes.
df_all['station'] = df_all['station'].astype('category').cat.codes.astype(int)
df_all['obs_type'] = df_all['obs_type'].astype('category').cat.codes.astype(int)
df_all['country_code'] = df_all['country_code'].astype('category').cat.codes.astype(int)

# Convert numerical columns to integers (round floats as needed):
# 'obs_value', 'TMAX_F'
df_all['obs_value'] = df_all['obs_value'].round(0).astype(int)
df_all['TMAX_F'] = df_all['TMAX_F'].round(0).astype(int)

# Ensure 'month' is integer type
df_all['month'] = df_all['month'].astype(int)

# Reorder columns to match target schema:
# ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']
df_final = df_all[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

# Write the transformed data to the specified CSV file without the index
output_path = 'autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_cot.csv'
df_final.to_csv(output_path, index=False)