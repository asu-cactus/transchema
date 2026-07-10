import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

union_0_2 = pd.concat([df0, df2], ignore_index=True)

join_1 = pd.merge(union_0_2, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

join_2 = pd.merge(join_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

result = join_2[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result['IsIntervention'] = result['IsIntervention'].fillna(0).astype(int)
result['IsInternational'] = result['IsInternational'].fillna(0).astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(str)
result['WarType'] = result['WarType'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)