import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")
result = merged[["Drug", "Timepoint", "Mouse ID"]].copy()
result["Timepoint"] = result["Timepoint"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv", index=False)