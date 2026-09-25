import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

union_result = pd.concat([df0, df2], ignore_index=True)

join_result_1 = pd.merge(union_result, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

join_result_2 = pd.merge(join_result_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

result = join_result_2[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)