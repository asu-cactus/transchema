import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

join_0 = pd.merge(s0, s2[['WarID','IsIntervention']], on='WarID', how='left')
join_1 = pd.merge(join_0, s3[['WarID','IsInternational']], on='WarID', how='left')

union_0_1 = pd.concat([s0, s1], ignore_index=True)

final_join = pd.merge(union_0_1, join_1[['WarID','WarType','WarShortName','IsInternational','IsIntervention']], on=['WarID','WarType','WarShortName'], how='left')

result = final_join[['WarType','WarID','WarShortName','IsInternational','IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)