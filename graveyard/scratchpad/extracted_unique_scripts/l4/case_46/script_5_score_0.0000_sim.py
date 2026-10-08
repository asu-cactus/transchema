import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)
union_0_2_1 = pd.concat([union_0_2, s1], ignore_index=True, sort=False)

df = pd.merge(union_0_2_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)
df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['WarID'] = df['WarID'].astype(int)
df['WarShortName'] = df['WarShortName'].astype(str)
df['WarType'] = df['WarType'].astype(int)

result = df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)