import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# Join s3 and s0 on WarID (left join to keep all from s3)
j0 = pd.merge(s3, s0, on="WarID", how="left", suffixes=('_3', '_0'))

# Join the result with s1 on WarID (left join to keep all from previous)
j1 = pd.merge(j0, s1[['WarID', 'IsIntervention']], on="WarID", how="left")

# Join the result with s2 on WarID (left join)
j2 = pd.merge(j1, s2[['WarID', 'WarShortName', 'WarType']], on="WarID", how="left", suffixes=('', '_2'))

# Now select columns for target schema:
# IsInternational from s3 (already in j2 as 'IsInternational')
# WarID
# WarShortName: prefer s2's WarShortName if exists, else s0's WarShortName
# WarType: prefer s2's WarType if exists, else s0's WarType
# IsIntervention from s1 (already in j2 as 'IsIntervention')

# Use s2's WarShortName and WarType if not null, else s0's
warshortname = j2['WarShortName'].combine_first(j2['WarShortName_0'])
wartype = j2['WarType'].combine_first(j2['WarType_0'])

df = pd.DataFrame({
    'IsInternational': j2['IsInternational'].fillna(0).astype(int),
    'WarID': j2['WarID'].astype(int),
    'WarShortName': warshortname,
    'WarType': wartype,
    'IsIntervention': j2['IsIntervention'].fillna(0).astype(int)
})

# Group by WarID to remove duplicates, take first for other columns
result = df.groupby('WarID', as_index=False).agg({
    'IsInternational': 'first',
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'first'
})

# Reorder columns to match target schema exactly
result = result[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)