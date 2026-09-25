import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1 (same schema)
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_0_1 with s2 on WarID (outer join to keep all)
join_1 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on="WarID", how="outer")

# JOIN join_1 with s3 on WarID (outer join)
join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on="WarID", how="outer")

# Fill missing IsInternational and IsIntervention with 0 for aggregation
join_2['IsInternational'] = join_2['IsInternational'].fillna(0).astype(int)
join_2['IsIntervention'] = join_2['IsIntervention'].fillna(0).astype(int)

# Group by WarType and aggregate counts and sums
result = join_2.groupby('WarType', dropna=False).agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
).reset_index()

# Ensure correct dtypes
result['WarType'] = result['WarType'].astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(int)
result['IsInternational'] = result['IsInternational'].astype(int)
result['IsIntervention'] = result['IsIntervention'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)