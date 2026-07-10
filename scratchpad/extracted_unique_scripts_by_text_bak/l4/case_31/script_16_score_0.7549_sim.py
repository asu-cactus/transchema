import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

join_1 = pd.merge(df2, df3, on="County", how="outer")
join_2 = pd.merge(join_1, df0, on="County", how="outer")
join_3 = pd.merge(join_2, df4, on="County", how="outer")
final = pd.merge(join_3, df1, on="County", how="outer")

final = final[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)