import pandas as pd

# File paths of sources
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_95/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_95/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_95/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_95/test_3.csv',
]

# List to store loaded DataFrames
dfs = []

# Load each source CSV with index_col=0 to ignore the first integer index column
for f in source_files:
    df = pd.read_csv(f, index_col=0)
    dfs.append(df)

# Concatenate all source dataframes (union)
combined_df = pd.concat(dfs, axis=0, ignore_index=True)

# Rearrange columns to match target schema order
target_columns = ['Subject', 'SubjectId', 'Split', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
combined_df = combined_df[target_columns]

# Ensure correct types
combined_df['Subject'] = combined_df['Subject'].astype(str)
combined_df['SubjectId'] = combined_df['SubjectId'].astype(int)
combined_df['Split'] = combined_df['Split'].astype(str)

for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    combined_df[col] = combined_df[col].astype(int)

# Export the result to the required path
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_95/target_multisource_cot.csv', index=False)