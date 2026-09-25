import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Country")

result = merged.groupby("Rank", as_index=False).size()
result.columns = ["Rank", "0"]
result["Rank"] = result["Rank"].astype(int)
result["0"] = result["0"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)