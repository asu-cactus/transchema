import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_41/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, left_on="Mouse ID", right_on="Mouse ID")

result = joined[["Drug", "Timepoint", "Metastatic Sites"]].copy()
result["Drug"] = result["Drug"].astype(str)
result["Timepoint"] = pd.to_numeric(result["Timepoint"], errors='coerce').astype('Int64')
result["Metastatic Sites"] = pd.to_numeric(result["Metastatic Sites"], errors='coerce').astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_41/target_multisource_mcts.csv", index=False)