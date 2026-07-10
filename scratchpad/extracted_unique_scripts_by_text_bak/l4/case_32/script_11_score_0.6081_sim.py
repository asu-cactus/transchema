import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

join1 = pd.merge(df3, df2, on="County", how="outer")
join2 = pd.merge(join1, df0, on="County", how="outer", suffixes=('_x', '_y'))
join3 = pd.merge(join2, df4, on="County", how="outer", suffixes=('_x', '_y'))
final_join = pd.merge(join3, df1, on="County", how="outer")

final_join = final_join.rename(columns={"r1403_x": "r1403_x", "r1403_y": "r1403_y", "r1401": "r1401", "r1402": "r1402"})

result = final_join.groupby(["County", "r1401", "r1402", "r1403_x", "r1403_y"], dropna=False).size().reset_index().drop(columns=0)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)