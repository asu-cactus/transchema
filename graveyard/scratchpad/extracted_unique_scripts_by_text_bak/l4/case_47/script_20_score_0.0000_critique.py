import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION Source0 and Source2 (same schema)
union_result = pd.concat([s0, s2], ignore_index=True)

# JOIN union_result with Source1 on WarID
join_result_1 = pd.merge(union_result, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN the above result with Source3 on WarID
join_result_2 = pd.merge(join_result_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Select and reorder columns as per target schema
result = join_result_2[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Fill missing IsIntervention and IsInternational with 0 (if any)
result['IsIntervention'] = result['IsIntervention'].fillna(0).astype(int)
result['IsInternational'] = result['IsInternational'].fillna(0).astype(int)

# Group by IsIntervention to remove duplicates if any
result = result.groupby(['IsIntervention'], as_index=False).first()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)