import pandas as pd

# List all source CSV file paths
source_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_90/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_90/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_90/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_90/test_3.csv"
]

# Read all source tables into pandas DataFrames, ignoring the first index column
source_dfs = [pd.read_csv(path, index_col=0) for path in source_paths]

# Select only the 'occluded' column from each source DataFrame
occluded_dfs = [df[['occluded']] for df in source_dfs]

# Concatenate all 'occluded' columns vertically (union)
target_df = pd.concat(occluded_dfs, ignore_index=True)

# Ensure the data type matches the target schema: integer
target_df['occluded'] = target_df['occluded'].astype(int)

# Output path
output_path = "autopipeline-benchmarks/github-pipelines/length4_90/target_multisource_cot.csv"

# Write the resulting DataFrame to CSV with header, without row index
target_df.to_csv(output_path, index=False)