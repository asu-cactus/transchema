import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Add missing 'IsIntervention' column to s0 and s2 with default 0 (assuming missing means 0)
s0['IsIntervention'] = 0
s2['IsIntervention'] = 0

# Select and reorder columns to match for union
cols = ['WarID', 'WarShortName', 'WarType', 'IsIntervention']
s0_sel = s0[cols]
s1_sel = s1[cols]
s2_sel = s2[cols]

# Union the three sources
unioned = pd.concat([s0_sel, s1_sel, s2_sel], ignore_index=True)

# Join with s3 on WarID to get IsInternational
joined = pd.merge(unioned, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsInternational with 0 as per hint 24 and target examples
joined['IsInternational'] = joined['IsInternational'].fillna(0).astype('Int64')

# Group by leftmost columns of target schema (keys)
grouped = joined.groupby(['IsIntervention', 'WarID', 'WarShortName', 'WarType'], as_index=False).agg(
    IsInternational=('IsInternational', 'max')
)

# Ensure correct dtypes as per target schema
grouped['IsIntervention'] = grouped['IsIntervention'].astype('Int64')
grouped['WarID'] = grouped['WarID'].astype('Int64')
grouped['WarShortName'] = grouped['WarShortName'].astype('Int64')
grouped['WarType'] = grouped['WarType'].astype('Int64')
grouped['IsInternational'] = grouped['IsInternational'].astype('Int64')

# Reorder columns to match target schema exactly
result = grouped[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)