import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

s0['IsIntervention'] = pd.NA
s2['IsIntervention'] = pd.NA

union_df = pd.concat([s0, s1, s2], ignore_index=True, sort=False)

result = pd.merge(union_df, s3[['WarID', 'IsInternational']], on='WarID', how='left')

result['IsIntervention'] = result['IsIntervention'].fillna(0).astype(int)
result['IsInternational'] = result['IsInternational'].fillna(0).astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(str)
result['WarType'] = result['WarType'].astype(int)

final = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)