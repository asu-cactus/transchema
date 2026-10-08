import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True)

join_0_1 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on='WarID', how='inner')

join_1_2 = pd.merge(join_0_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

target = join_1_2[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)