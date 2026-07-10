import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

merged = pd.merge(df0, df2, left_on="Country", right_on="Country Name", how="inner")

grouped = merged.groupby("Rank", as_index=False).size()

result = grouped.rename(columns={"size": "0"})
result["0"] = result["0"].astype(int)
result["Rank"] = result["Rank"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)