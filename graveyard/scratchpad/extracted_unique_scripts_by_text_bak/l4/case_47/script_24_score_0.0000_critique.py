import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Add missing IsIntervention column to s0 and s2 with default 0 (integer)
s0['IsIntervention'] = 0
s2['IsIntervention'] = 0

# Select columns to match s1 schema for union
cols = ['WarID', 'WarShortName', 'WarType', 'IsIntervention']

s0_sel = s0[cols]
s1_sel = s1[cols]
s2_sel = s2[cols]

# Union s0, s1, s2
union012 = pd.concat([s0_sel, s1_sel, s2_sel], ignore_index=True)

# Join union012 with s3 on WarID to get IsInternational
# s3 has columns: WarID, WarShortName, WarType, IsInternational
# We only need WarID and IsInternational from s3 to avoid duplicate columns
s3_sel = s3[['WarID', 'IsInternational']]

joined = pd.merge(union012, s3_sel, on='WarID', how='inner')

# Group by IsIntervention and WarID, aggregate other columns by first
result = joined.groupby(['IsIntervention', 'WarID'], as_index=False).agg({
    'WarShortName': 'first',
    'WarType': 'first',
    'IsInternational': 'first'
})

# Reorder columns to match target schema exactly
result = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)