import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# Join s0 and s1 on WarID
join_01 = pd.merge(s0, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# Join with s2 on WarID
join_012 = pd.merge(join_01, s2[['WarID', 'WarShortName', 'WarType']], on='WarID', how='inner', suffixes=('_01', '_2'))

# Join with s3 on WarID
join_all = pd.merge(join_012, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Fill missing IsInternational and IsIntervention with 0
join_all['IsInternational'] = join_all['IsInternational'].fillna(0).astype(int)
join_all['IsIntervention'] = join_all['IsIntervention'].fillna(0).astype(int)

# For WarShortName and WarType, prefer values from s0 or s1 or s2 (choose one source consistently)
# Since s0 and s2 have WarShortName and WarType, s1 only has IsIntervention extra
# Use WarShortName and WarType from s0 if available, else s2

# Because after join, we have WarShortName_01 (from s0) and WarShortName (from s2)
# Use WarShortName_01 if not null, else WarShortName (from s2)
join_all['WarShortName'] = join_all['WarShortName_01'].combine_first(join_all['WarShortName'])

# Similarly for WarType
join_all['WarType'] = join_all['WarType_01'].combine_first(join_all['WarType'])

# Convert WarShortName to integer by factorizing (mapping unique strings to unique integers)
join_all['WarShortName'] = pd.factorize(join_all['WarShortName'])[0]

# Ensure WarID and WarType are integers
join_all['WarID'] = join_all['WarID'].astype(int)
join_all['WarType'] = join_all['WarType'].astype(int)

# Select and reorder columns as per target schema
result = join_all[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)