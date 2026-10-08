import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

join_1_3 = pd.merge(s1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

union_0_2 = pd.concat([s0, s2], ignore_index=True)

final = pd.merge(union_0_2, join_1_3, on='WarID', how='inner')

final = final[['IsIntervention', 'WarID', 'WarShortName_x', 'WarType_x', 'IsInternational']]
final.columns = ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']

final['IsIntervention'] = final['IsIntervention'].fillna(0).astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype(int)
final['IsInternational'] = final['IsInternational'].fillna(0).astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)