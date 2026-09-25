import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)

merged = pd.merge(df2, df0, left_on="Country", right_on="Country Name")

grouped = merged.groupby("Rank").size().reset_index(name='0')

grouped["Rank"] = grouped["Rank"].astype(int)
grouped["0"] = grouped["0"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)