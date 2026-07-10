import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

union_result = pd.concat([s0, s2], ignore_index=True)

join_result = pd.merge(union_result, s3[['WarID', 'IsInternational']], on='WarID', how='left')

final_join = pd.merge(join_result, s1[['WarID', 'IsIntervention']], on='WarID', how='left')

final = final_join[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

final['IsInternational'] = final['IsInternational'].fillna(0).astype(int)
final['IsIntervention'] = final['IsIntervention'].fillna(0).astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)