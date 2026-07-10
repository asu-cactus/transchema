import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_23 = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))

union_014 = pd.concat([s0, s1, s4], ignore_index=True)

final = pd.merge(union_014, join_23, on="hero", how="inner", suffixes=('', '_joined'))

final = final[['hero', 'disadvantage', 'winrate', 'matches']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)