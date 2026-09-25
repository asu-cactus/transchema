import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Extract numeric part of Mouse ID and convert to int
df_merged["Mouse ID"] = df_merged["Mouse ID"].astype(str).str.extract('(\d+)').astype(int)

# Select relevant columns
df_result = df_merged[["Drug", "Timepoint", "Mouse ID"]]

# Group by Drug, Timepoint, Mouse ID and count occurrences to remove duplicates
df_result = df_result.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size()

# Rename the count column to something neutral or drop it since target schema has only 3 columns
# The target schema has only Drug, Timepoint, Mouse ID, so drop the count column
df_result = df_result.drop(columns=["size"])

# Ensure types
df_result["Timepoint"] = df_result["Timepoint"].astype(int)
df_result["Mouse ID"] = df_result["Mouse ID"].astype(int)
df_result["Drug"] = df_result["Drug"].astype(str)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)