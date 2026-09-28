import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID", how="inner")

df = df[["Drug", "Timepoint", "Mouse ID"]]

df["Timepoint"] = pd.to_numeric(df["Timepoint"], errors='coerce').astype('Int64')

df = df.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size().drop(columns="size", errors='ignore')  # size() returns a Series, so use groupby().first() instead

# Since no aggregation is needed, just drop duplicates:
df = df.drop_duplicates(subset=["Drug", "Timepoint", "Mouse ID"])

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)