import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

join_0 = pd.merge(df3, df0, on="County", how="inner")
join_1 = pd.merge(join_0, df1, on="County", how="inner")
join_2 = pd.merge(join_1, df2, on="County", how="inner")

result = join_2.groupby(["County", "r1401", "r1403"], as_index=False).size()
result = result.drop(columns=["size"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)