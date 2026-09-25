import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv", index_col=0)

# Join on Mouse ID (string)
merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, aggregate count of Mouse ID
grouped = merged.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": "count"})

# Ensure types match target schema
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mouse ID"] = grouped["Mouse ID"].astype(int)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv", index=False)