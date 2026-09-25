import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION s0 and s2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)

# JOIN union_0_2 with s1 on WarID to add IsIntervention
union_0_2_1 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN the above with s3 on WarID to add IsInternational
df = pd.merge(union_0_2_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Cast columns to correct types and order columns as per target schema
df['IsInternational'] = df['IsInternational'].astype(int)
df['IsIntervention'] = df['IsIntervention'].astype(int)
df['WarID'] = df['WarID'].astype(int)
df['WarShortName'] = df['WarShortName'].astype(str)
df['WarType'] = df['WarType'].astype(int)

result = df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)