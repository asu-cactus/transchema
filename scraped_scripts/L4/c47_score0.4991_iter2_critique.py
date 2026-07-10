import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Union Source0 and Source2 (both have same schema)
union_0_2 = pd.concat([df0, df2], ignore_index=True, sort=False)

# Join union_0_2 with Source1 on WarID (left join to keep all wars)
join_0_2_1 = pd.merge(union_0_2, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

# Join the above with Source3 on WarID (left join)
final_join = pd.merge(join_0_2_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsIntervention and IsInternational with 0
final_join['IsIntervention'] = final_join['IsIntervention'].fillna(0).astype(int)
final_join['IsInternational'] = final_join['IsInternational'].fillna(0).astype(int)

# Select and reorder columns as per target schema
result = final_join[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Ensure correct types
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(str)
result['WarType'] = result['WarType'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)