import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION Source4_46_0 and Source4_46_2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# JOIN union_0_2 with s1 on WarID
join_1 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN join_1 with s3 on WarID
join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Factorize WarShortName to integer codes (consistent)
# Combine all WarShortName values from union_0_2, s1, s3 to get consistent mapping
# But s1 and s3 have WarShortName columns too, but we only kept WarShortName from union_0_2
# So factorize on join_2['WarShortName']
join_2['WarShortName'] = pd.factorize(join_2['WarShortName'])[0]

# Group by IsInternational and WarID, aggregate by first for other columns
result = join_2.groupby(['IsInternational', 'WarID'], as_index=False).agg({
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'first'
})

# Reorder columns to match target schema
result = result[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Ensure all columns are int64
result = result.astype({
    'IsInternational': 'int64',
    'WarID': 'int64',
    'WarShortName': 'int64',
    'WarType': 'int64',
    'IsIntervention': 'int64'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)