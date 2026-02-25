import pandas as pd

# File paths for all source CSV files
path_source0 = 'autopipeline-benchmarks/github-pipelines/length4_32/test_0.csv'  # County, r1403
path_source1 = 'autopipeline-benchmarks/github-pipelines/length4_32/test_1.csv'  # County
path_source2 = 'autopipeline-benchmarks/github-pipelines/length4_32/test_2.csv'  # County, r1402
path_source3 = 'autopipeline-benchmarks/github-pipelines/length4_32/test_3.csv'  # County, r1401
path_source4 = 'autopipeline-benchmarks/github-pipelines/length4_32/test_4.csv'  # County, r1403

# Load all sources with index_col=0 to ignore numerical index column
df0 = pd.read_csv(path_source0, index_col=0)  # Source0
df1 = pd.read_csv(path_source1, index_col=0)  # Source1
df2 = pd.read_csv(path_source2, index_col=0)  # Source2
df3 = pd.read_csv(path_source3, index_col=0)  # Source3
df4 = pd.read_csv(path_source4, index_col=0)  # Source4

# Rename r1403 columns in df0 and df4 to avoid collision and match target schema
df0 = df0.rename(columns={'r1403': 'r1403_x'})
df4 = df4.rename(columns={'r1403': 'r1403_y'})

# Start with df1 as the master county list to keep all counties
result = df1.copy()

# Join r1401 from df3 (left join to keep all counties)
result = result.merge(df3[['County', 'r1401']], on='County', how='left')

# Join r1402 from df2
result = result.merge(df2[['County', 'r1402']], on='County', how='left')

# Join r1403_x from df0
result = result.merge(df0[['County', 'r1403_x']], on='County', how='left')

# Join r1403_y from df4
result = result.merge(df4[['County', 'r1403_y']], on='County', how='left')

# Replace any missing values with 'NR'
result = result.fillna('NR')

# Ensure all relevant columns are strings (also County)
for col in ['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']:
    result[col] = result[col].astype(str)

# Reorder columns to match target schema exactly
result = result[['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']]

# Save the final table to csv without the index
output_path = 'autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_cot.csv'
result.to_csv(output_path, index=False)