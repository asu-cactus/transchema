import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

# Start from Source3_85_3 (County subset)
join_1 = pd.merge(df3, df2, on="County", how="left")
join_2 = pd.merge(join_1, df0, on="County", how="left")
join_3 = pd.merge(join_2, df1, on="County", how="left")

result = join_3[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)