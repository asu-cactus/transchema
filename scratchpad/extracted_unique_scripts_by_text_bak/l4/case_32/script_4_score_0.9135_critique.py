import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

join_04 = pd.merge(s0, s4, on="County", suffixes=('_x', '_y'))
join_043 = pd.merge(join_04, s3, on="County")
join_0432 = pd.merge(join_043, s2, on="County")
final = pd.merge(join_0432, s1, on="County")

final = final[['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv")