import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION Source0 and Source2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# JOIN union_0_2 with Source1 on WarID
join_01 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN the above with Source3 on WarID
join_013 = pd.merge(join_01, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Select columns as per target schema
result = join_013[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)