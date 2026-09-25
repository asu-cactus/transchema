import pandas as pd

# Define file paths for the source CSV files
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_65/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_65/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_65/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_65/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length4_65/test_4.csv',
]

# List to hold DataFrames
dfs = []

# Load each source file into a DataFrame
for file in source_files:
    # index_col=0 to ignore the numerical index column
    df = pd.read_csv(file, index_col=0)
    dfs.append(df)

# Concatenate all source DataFrames (union operation)
union_df = pd.concat(dfs, ignore_index=True)

# Ensure columns order matches the target schema exactly
target_columns = ['Year', 'Category', 'Nominee', 'Movie', 'Winner']
union_df = union_df[target_columns]

# Convert all columns to string, as target schema expects string types
for col in target_columns:
    union_df[col] = union_df[col].astype(str)

# Write the resulting DataFrame to the target CSV file path (without index)
output_path = 'autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_cot.csv'
union_df.to_csv(output_path, index=False)