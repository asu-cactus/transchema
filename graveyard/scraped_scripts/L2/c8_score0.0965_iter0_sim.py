import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

df = df[["Drug", "Timepoint", "Mouse ID"]]

df["Timepoint"] = pd.to_numeric(df["Timepoint"], errors='coerce').astype('Int64')
df["Mouse ID"] = pd.to_numeric(df["Mouse ID"], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)