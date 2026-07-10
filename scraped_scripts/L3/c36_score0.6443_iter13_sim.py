import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)

union_1 = pd.concat([df1, df1], ignore_index=True)
union_2 = pd.concat([df2, df2], ignore_index=True)

join_12 = pd.merge(union_1, union_2, on="County", how="outer")
join_all = pd.merge(join_12, df0, on="County", how="outer")

result = join_all.rename(columns={"m1402": "m1403"})
result = result[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)