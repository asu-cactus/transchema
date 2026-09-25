import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="Mouse ID")
result = merged[["Drug", "Timepoint", "Mouse ID"]]

result["Drug"] = result["Drug"].astype(str)
result["Timepoint"] = pd.to_numeric(result["Timepoint"], errors='coerce').astype('Int64')
result["Mouse ID"] = pd.to_numeric(result["Mouse ID"], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)