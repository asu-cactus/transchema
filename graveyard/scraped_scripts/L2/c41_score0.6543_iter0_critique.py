import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_41/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Select relevant columns
selected = joined[["Drug", "Timepoint", "Metastatic Sites"]].copy()

# Convert types as per target schema
selected["Drug"] = selected["Drug"].astype(str)
selected["Timepoint"] = pd.to_numeric(selected["Timepoint"], errors='coerce').astype('Int64')
selected["Metastatic Sites"] = pd.to_numeric(selected["Metastatic Sites"], errors='coerce').astype(float)

# Group by Drug and Timepoint, aggregate Metastatic Sites by mean
result = selected.groupby(["Drug", "Timepoint"], as_index=False).agg({"Metastatic Sites": "mean"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_41/target_multisource_mcts.csv", index=False)