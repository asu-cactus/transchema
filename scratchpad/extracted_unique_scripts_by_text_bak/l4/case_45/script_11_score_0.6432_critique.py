import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1 (same schema)
unioned = pd.concat([s0, s1], ignore_index=True).drop_duplicates(subset=['WarID'])

# JOIN unioned with s2 and s3 on WarID to get IsIntervention and IsInternational
df = unioned.merge(s2[['WarID', 'IsIntervention']], on='WarID', how='left')
df = df.merge(s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill NaN in IsIntervention and IsInternational with 0 (flags)
df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)

# Group by WarType and aggregate counts and sums
result = df.groupby('WarType', as_index=False).agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
)

# Ensure correct dtypes
result['WarType'] = result['WarType'].astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(int)
result['IsInternational'] = result['IsInternational'].astype(int)
result['IsIntervention'] = result['IsIntervention'].astype(int)

# Reorder columns to match target schema
result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)