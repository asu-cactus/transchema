import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# Add missing columns with 0 for union compatibility
s0['IsInternational'] = 0
s0['IsIntervention'] = 0

s1['IsInternational'] = 0
s1['IsIntervention'] = 0

s2['IsInternational'] = 0  # s2 has IsIntervention but no IsInternational

s3['IsIntervention'] = 0  # s3 has IsInternational but no IsIntervention

# Select columns in the same order for union
cols = ['WarID', 'WarShortName', 'WarType', 'IsInternational', 'IsIntervention']

df0 = s0[cols]
df1 = s1[cols]
df2 = s2[cols]
df3 = s3[cols]

# Union all sources
union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by WarType and aggregate counts and sums
result = union_df.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
).reset_index()

# Reorder columns to match target schema
result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Ensure integer types
result = result.astype({
    'WarType': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'IsInternational': 'Int64',
    'IsIntervention': 'Int64'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)