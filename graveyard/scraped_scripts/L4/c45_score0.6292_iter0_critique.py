import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION s0 and s1 (same schema)
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_0_1 with s2 on WarID (left join to keep all wars)
join_0_2 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN join_0_2 with s3 on WarID (left join)
join_0_3 = pd.merge(join_0_2, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# GROUP BY WarType and aggregate counts of WarID, WarShortName, IsInternational, IsIntervention
result = join_0_3.groupby('WarType', dropna=False).agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'count'),
    IsIntervention=('IsIntervention', 'count')
).reset_index()

# Reorder columns to match target schema
result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)