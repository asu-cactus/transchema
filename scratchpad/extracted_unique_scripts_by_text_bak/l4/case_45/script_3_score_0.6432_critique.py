import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1 (same schema)
union_01 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_01 with Source2 on WarID
join_1 = pd.merge(union_01, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN join_1 with Source3 on WarID
join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Replace NaN in IsInternational and IsIntervention with 0 (no intervention/international flag)
join_2['IsInternational'] = pd.to_numeric(join_2['IsInternational'], errors='coerce').fillna(0).astype(int)
join_2['IsIntervention'] = pd.to_numeric(join_2['IsIntervention'], errors='coerce').fillna(0).astype(int)

# Group by WarType and aggregate counts and sums
result = join_2.groupby('WarType', as_index=False).agg({
    'WarID': 'count',           # count of WarID per WarType
    'WarShortName': 'count',    # count of WarShortName per WarType (same as WarID count)
    'IsInternational': 'sum',   # sum of IsInternational per WarType
    'IsIntervention': 'sum'     # sum of IsIntervention per WarType
})

# Ensure all columns are int type
for col in ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']:
    result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)