import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Union Source0 and Source2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# Join Source1 and Source3 on WarID
join_1_3 = pd.merge(s1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Join union_0_2 with join_1_3 on WarID
final = pd.merge(union_0_2, join_1_3, on='WarID', how='inner')

# Select and rename columns to match target schema
final = final[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Fill missing IsIntervention and IsInternational with 0 and cast types
final['IsIntervention'] = final['IsIntervention'].fillna(0).astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype(int)
final['IsInternational'] = final['IsInternational'].fillna(0).astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)