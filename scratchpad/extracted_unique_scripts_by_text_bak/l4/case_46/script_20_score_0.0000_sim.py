import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

join_3_1 = pd.merge(s3, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

union_0_2 = pd.concat([s0, s2], ignore_index=True)

final = pd.merge(union_0_2, join_3_1, on='WarID', how='inner')

final = final[['IsInternational', 'WarID', 'WarShortName_x', 'WarType_x', 'IsIntervention']]
final.columns = ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']

final['IsInternational'] = final['IsInternational'].astype('Int64')
final['WarID'] = final['WarID'].astype('Int64')
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype('Int64')
final['IsIntervention'] = final['IsIntervention'].astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)