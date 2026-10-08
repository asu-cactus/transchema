import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION s0 and s2 (same schema)
u0_2 = pd.concat([s0, s2], ignore_index=True)

# UNION s1 and s3 (same schema)
u1_3 = pd.concat([s1, s3], ignore_index=True)

# Join on WarID
merged = pd.merge(u0_2, u1_3[['WarID', 'IsInternational', 'IsIntervention']], on='WarID', how='inner')

# Map WarShortName strings to integers (consistent with target examples)
# Use factorize to assign unique integer IDs to WarShortName
warshortname_codes, uniques = pd.factorize(merged['WarShortName'])
merged['WarShortName'] = warshortname_codes

# Ensure all columns have correct types as per target schema
result = merged[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']].copy()

result = result.astype({
    'IsInternational': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'WarType': 'Int64',
    'IsIntervention': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)