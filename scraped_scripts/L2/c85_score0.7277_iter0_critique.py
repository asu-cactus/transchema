import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv", index_col=0)

# Join on Mouse ID (string)
df = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, aggregate count of Mouse ID
df_grouped = df.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": "count"})

# Convert columns to target types
df_grouped["Drug"] = df_grouped["Drug"].astype(str)
df_grouped["Timepoint"] = pd.to_numeric(df_grouped["Timepoint"], errors='coerce').astype('Int64')
df_grouped["Mouse ID"] = pd.to_numeric(df_grouped["Mouse ID"], errors='coerce').astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv", index=False)