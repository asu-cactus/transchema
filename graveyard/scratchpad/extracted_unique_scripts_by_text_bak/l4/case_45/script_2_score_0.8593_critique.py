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
s3['IsIntervention'] = 0   # s3 has IsInternational but no IsIntervention

# Concatenate all sources
union_all = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Ensure correct types
union_all['WarType'] = union_all['WarType'].astype(int)
union_all['WarID'] = union_all['WarID'].astype(int)
union_all['WarShortName'] = union_all['WarShortName'].astype(str)  # keep as string for now
union_all['IsInternational'] = union_all['IsInternational'].astype(int)
union_all['IsIntervention'] = union_all['IsIntervention'].astype(int)

# Group by WarType and aggregate
result = union_all.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
).reset_index()

# Reorder columns to match target schema
result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)