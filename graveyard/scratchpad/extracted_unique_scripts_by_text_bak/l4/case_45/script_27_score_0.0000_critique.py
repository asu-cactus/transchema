import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source4_45_0 and Source4_45_1 (same schema)
union_01 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_01 with Source4_45_2 on WarID (inner join)
join_012 = pd.merge(union_01, s2, on="WarID", how="inner", suffixes=('', '_2'))

# JOIN join_012 with Source4_45_3 on WarID (inner join)
join_0123 = pd.merge(join_012, s3, on="WarID", how="inner", suffixes=('', '_3'))

# Hash WarShortName before aggregation
join_0123['WarShortName_hashed'] = join_0123['WarShortName'].apply(lambda x: hash(x) % (10**9))

# Group by WarType (from union_01, which is the same as WarType in join_0123)
grouped = join_0123.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName_hashed', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
).reset_index()

# Ensure correct dtypes
grouped['WarType'] = grouped['WarType'].astype('Int64')
grouped['WarID'] = grouped['WarID'].astype('Int64')
grouped['WarShortName'] = grouped['WarShortName'].astype('Int64')
grouped['IsInternational'] = grouped['IsInternational'].astype('Int64')
grouped['IsIntervention'] = grouped['IsIntervention'].astype('Int64')

# Reorder columns to match target schema
result = grouped[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)