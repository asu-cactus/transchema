import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Add missing IsIntervention column to s0 and s2 with NaN
s0['IsIntervention'] = pd.NA
s2['IsIntervention'] = pd.NA

# Union s0, s1, s2 (schemas aligned)
unioned = pd.concat([s0, s1, s2], ignore_index=True, sort=False)

# Fill missing IsIntervention with 0 (assuming missing means 0)
unioned['IsIntervention'] = unioned['IsIntervention'].fillna(0).astype(int)

# Join unioned with s3 on WarID to get IsInternational
df = pd.merge(unioned, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsInternational with 0
df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)

# Convert WarShortName to integer by factorizing (to match target integer type)
df['WarShortName'] = pd.factorize(df['WarShortName'])[0].astype(int)

# WarType is already integer, ensure type
df['WarType'] = df['WarType'].astype(int)

# Ensure IsIntervention and WarID are integer
df['IsIntervention'] = df['IsIntervention'].astype(int)
df['WarID'] = df['WarID'].astype(int)

# Select and reorder columns as per target schema
df = df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)