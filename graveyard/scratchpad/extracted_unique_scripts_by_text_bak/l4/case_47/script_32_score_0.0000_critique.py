import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Union Source4_47_0 and Source4_47_2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)

# Join union with Source4_47_1 on WarID
join_0_1 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# Join above with Source4_47_3 on WarID
join_1_3 = pd.merge(join_0_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Convert columns to appropriate types, fill missing with 0
df = join_1_3.copy()

df['IsIntervention'] = pd.to_numeric(df['IsIntervention'], errors='coerce').fillna(0).astype(int)
df['IsInternational'] = pd.to_numeric(df['IsInternational'], errors='coerce').fillna(0).astype(int)
df['WarShortName'] = pd.to_numeric(df['WarShortName'], errors='coerce').fillna(0).astype(int)
df['WarType'] = pd.to_numeric(df['WarType'], errors='coerce').fillna(0).astype(int)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').fillna(0).astype(int)

# Group by WarID, aggregate other columns by max
agg_df = df.groupby('WarID', as_index=False).agg({
    'IsIntervention': 'max',
    'WarShortName': 'max',
    'WarType': 'max',
    'IsInternational': 'max'
})

# Reorder columns to match target schema
agg_df = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)