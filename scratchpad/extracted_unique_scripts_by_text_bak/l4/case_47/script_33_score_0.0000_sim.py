import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

r1 = pd.merge(s0, s1[['WarID']], on='WarID', how='inner')
r2 = pd.merge(r1, s2[['WarID']], on='WarID', how='inner')
r3 = pd.merge(r2, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

final = pd.merge(r3, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

final = final[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final['IsIntervention'] = final['IsIntervention'].astype('Int64')
final['WarID'] = final['WarID'].astype('Int64')
final['WarShortName'] = final['WarShortName'].astype('Int64', errors='ignore') if final['WarShortName'].dtype != 'int64' else final['WarShortName']
final['WarType'] = final['WarType'].astype('Int64')
final['IsInternational'] = final['IsInternational'].astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)