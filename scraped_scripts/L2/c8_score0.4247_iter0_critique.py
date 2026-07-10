import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

# Inner join on Mouse ID
df = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Select relevant columns
df = df[["Drug", "Timepoint", "Mouse ID"]]

# Convert Mouse ID strings to integer codes (consistent mapping)
df["Mouse ID"] = df["Mouse ID"].astype('category').cat.codes.astype('Int64')

# Convert Timepoint to integer type
df["Timepoint"] = pd.to_numeric(df["Timepoint"], errors='coerce').astype('Int64')

# Group by all three columns to get unique rows (no aggregation)
df = df.drop_duplicates(subset=["Drug", "Timepoint", "Mouse ID"])

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)