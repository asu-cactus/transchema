import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

# Extract numeric part of Mouse ID and convert to int in both tables for consistent join keys
df0["Mouse ID"] = df0["Mouse ID"].str.extract('(\d+)').astype(int)
df1["Mouse ID"] = df1["Mouse ID"].str.extract('(\d+)').astype(int)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Ensure Timepoint is integer
df_merged["Timepoint"] = df_merged["Timepoint"].astype(int)

# Select columns in target schema order
result = df_merged[["Drug", "Timepoint", "Mouse ID"]]

# Remove duplicates by grouping on all columns (equivalent to distinct)
result = result.drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)