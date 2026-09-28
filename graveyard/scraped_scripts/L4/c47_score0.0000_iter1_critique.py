import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION s0 and s2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)

# JOIN union_0_2 with s1 on WarID, WarShortName, WarType (to get IsIntervention)
join_1 = pd.merge(
    union_0_2,
    s1[['WarID', 'WarShortName', 'WarType', 'IsIntervention']],
    on=['WarID', 'WarShortName', 'WarType'],
    how='inner'
)

# JOIN the above with s3 on WarID, WarShortName, WarType (to get IsInternational)
join_2 = pd.merge(
    join_1,
    s3[['WarID', 'WarShortName', 'WarType', 'IsInternational']],
    on=['WarID', 'WarShortName', 'WarType'],
    how='inner'
)

# Group by IsIntervention, aggregate other columns by max (since they are identical per group)
agg_df = join_2.groupby('IsIntervention', as_index=False).agg({
    'WarID': 'max',
    'WarShortName': 'max',
    'WarType': 'max',
    'IsInternational': 'max'
})

# Reorder columns to match target schema
result = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Ensure correct types
result['IsIntervention'] = result['IsIntervention'].astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(str)
result['WarType'] = result['WarType'].astype(int)
result['IsInternational'] = result['IsInternational'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)