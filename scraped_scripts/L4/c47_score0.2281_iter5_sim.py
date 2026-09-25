import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

union_0_2 = pd.concat([s0, s2], ignore_index=True)

join_1 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on='WarID', how='left')
join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

join_2['WarShortName'] = join_2['WarShortName'].astype('string')
join_2['WarType'] = join_2['WarType'].astype('Int64')
join_2['IsIntervention'] = join_2['IsIntervention'].fillna(0).astype('Int64')
join_2['IsInternational'] = join_2['IsInternational'].fillna(0).astype('Int64')

join_2['WarID'] = join_2['WarID'].astype('Int64')

join_2['WarShortName'] = join_2['WarShortName'].map(join_2.groupby('WarShortName')['WarShortName'].ngroup())

result = join_2[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)