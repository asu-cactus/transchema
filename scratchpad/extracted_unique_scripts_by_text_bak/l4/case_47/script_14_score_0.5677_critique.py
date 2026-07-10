import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Join Source0 and Source1 on WarID
df = pd.merge(s0, s1[['WarID', 'IsIntervention']], on='WarID', how='outer')

# Join with Source2 on WarID
df = pd.merge(df, s2[['WarID', 'WarShortName', 'WarType']], on='WarID', how='outer', suffixes=('', '_s2'))

# Join with Source3 on WarID
df = pd.merge(df, s3[['WarID', 'IsInternational']], on='WarID', how='outer')

# For WarShortName and WarType, prefer values from s0 or s2 (s0 first, then s2)
# Fill missing WarShortName from s2 if missing in s0
df['WarShortName'] = df['WarShortName'].combine_first(df['WarShortName_s2'])
df['WarType'] = df['WarType'].combine_first(df['WarType_s2'])

# Drop the extra columns from s2
df = df.drop(columns=['WarShortName_s2', 'WarType_s2'])

# Fill missing IsIntervention and IsInternational with 0 and convert to int
df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)

# WarID and WarType to int
df['WarID'] = df['WarID'].astype(int)
df['WarType'] = df['WarType'].astype(int)

# WarShortName is string, keep as is (no numeric conversion)
# Select columns in target schema order
target = df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)