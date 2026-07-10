import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

# Join on Mouse ID (string)
df_merged = pd.merge(df0, df1, on="Mouse ID")

# Group by Drug and Timepoint, count Mouse ID occurrences
df_grouped = df_merged.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": "count"})

# Rename columns to match target schema
# Drug: string, Timepoint: int, Mouse ID: int (count)
df_grouped["Timepoint"] = df_grouped["Timepoint"].astype(int)
df_grouped["Mouse ID"] = df_grouped["Mouse ID"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)