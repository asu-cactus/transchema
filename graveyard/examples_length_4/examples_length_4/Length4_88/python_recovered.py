import pandas as pd

# Source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_88/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_88/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_88/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_88/test_3.csv"
]

# List to collect DataFrames
dfs = []

# Load each source file, reading with index_col=0, extract TrackID column only
for filepath in source_files:
    df = pd.read_csv(filepath, index_col=0)
    dfs.append(df[['TrackID']])

# Concatenate all TrackID columns (union)
combined_df = pd.concat(dfs, ignore_index=True)

# Drop duplicates to match unique TrackID values in the target
combined_df = combined_df.drop_duplicates()

# Ensure TrackID is integer type as per target schema
combined_df['TrackID'] = combined_df['TrackID'].astype(int)

# Sort by TrackID ascending (optional, for tidiness and verification)
combined_df = combined_df.sort_values('TrackID').reset_index(drop=True)

# Output file path
output_path = "autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_cot.csv"

# Save to CSV without index
combined_df.to_csv(output_path, index=False)