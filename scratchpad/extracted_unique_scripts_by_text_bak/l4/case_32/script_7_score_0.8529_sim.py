import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

join_34 = pd.merge(s3, s4, on="County", suffixes=('_x', '_y'))
join_340 = pd.merge(join_34, s0, on="County")
final = pd.merge(join_340, s2, on="County")

final = final[['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv")