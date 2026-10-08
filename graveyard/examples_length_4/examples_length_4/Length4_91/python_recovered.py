import pandas as pd

# Define paths for source CSV files
source_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_91/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/test_3.csv",
]

# Load each source CSV, extracting 'attributes' column
attributes_dfs = []
for path in source_paths:
    df = pd.read_csv(path, index_col=0)
    # Select only the 'attributes' column
    attributes_only = df[['attributes']]
    attributes_dfs.append(attributes_only)

# Concatenate all attributes columns vertically (union all rows)
all_attributes = pd.concat(attributes_dfs, ignore_index=True)

# Remove rows where 'attributes' is NaN or empty string
all_attributes_cleaned = all_attributes.dropna(subset=['attributes'])
all_attributes_cleaned = all_attributes_cleaned[all_attributes_cleaned['attributes'].str.strip() != ""]

# Drop duplicates to get distinct attributes as per target examples
distinct_attributes = all_attributes_cleaned.drop_duplicates().reset_index(drop=True)

# Optional: sort attributes alphabetically to have stable order (not mandatory)
distinct_attributes_sorted = distinct_attributes.sort_values('attributes').reset_index(drop=True)

# Write output CSV to the target path with header
distinct_attributes_sorted.to_csv(
    "autopipeline-benchmarks/github-pipelines/length4_91/target_multisource_cot.csv",
    index=False,
    header=True
)