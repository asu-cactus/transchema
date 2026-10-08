import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Join s0 and s1 on WarID
join_01 = pd.merge(s0, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# Join the result with s2 on WarID
join_012 = pd.merge(join_01, s2[['WarID', 'WarShortName', 'WarType']], on='WarID', how='inner', suffixes=('_01', '_2'))

# Since s0 and s2 have WarShortName and WarType, keep s0's WarShortName and WarType (from join_01)
# But s2's WarShortName and WarType may be duplicates, so we can ignore s2's columns or verify consistency.
# To avoid confusion, drop s2's WarShortName and WarType after join.
join_012 = join_012.drop(columns=['WarShortName', 'WarType'])

# Join with s3 on WarID
join_all = pd.merge(join_012, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Now we have columns: WarID, WarShortName, WarType, IsIntervention, IsInternational
# But WarShortName and WarType come from s0 (original), IsIntervention from s1, IsInternational from s3

# Group by WarID to ensure uniqueness and aggregate
agg_df = join_all.groupby('WarID').agg({
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'max',
    'IsInternational': 'max'
}).reset_index()

# Reorder columns to match target schema: ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']
final_df = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write to CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)