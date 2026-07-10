import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Join s0 and s1 on WarID (inner join to keep only matching WarIDs)
join_0_1 = pd.merge(s0, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# Join the above with s2 on WarID
join_0_1_2 = pd.merge(join_0_1, s2[['WarID', 'WarShortName', 'WarType']], on='WarID', how='inner', suffixes=('_01', '_2'))

# Join the above with s3 on WarID
join_all = pd.merge(join_0_1_2, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Group by WarID and aggregate
# For IsIntervention and IsInternational take max (flags)
# For WarShortName and WarType take first non-null from s0/s2 (prefer s0)
# Since WarShortName in target is integer equal to WarID, set WarShortName = WarID
agg_df = join_all.groupby('WarID').agg({
    'IsIntervention': 'max',
    'IsInternational': 'max',
    'WarShortName_01': 'first',
    'WarType_01': 'first'
}).reset_index()

# Rename columns to target schema
agg_df = agg_df.rename(columns={
    'WarShortName_01': 'WarShortName',
    'WarType_01': 'WarType'
})

# According to target examples, WarShortName is integer equal to WarID
# So replace WarShortName with WarID
agg_df['WarShortName'] = agg_df['WarID']

# Ensure correct dtypes
agg_df['IsIntervention'] = agg_df['IsIntervention'].astype('Int64')
agg_df['WarID'] = agg_df['WarID'].astype('Int64')
agg_df['WarShortName'] = agg_df['WarShortName'].astype('Int64')
agg_df['WarType'] = agg_df['WarType'].astype('Int64')
agg_df['IsInternational'] = agg_df['IsInternational'].astype('Int64')

# Reorder columns as per target schema
final = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)