import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Join s0 and s1 on WarID
df01 = pd.merge(s0, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# Join the result with s2 on WarID
df012 = pd.merge(df01, s2[['WarID', 'WarShortName', 'WarType']], on='WarID', how='inner', suffixes=('', '_s2'))

# Since s0 and s2 have WarShortName and WarType, but s0 and s1 already have them,
# we keep the columns from s0/s1 and ignore s2's duplicates.
# So drop s2's WarShortName_s2 and WarType_s2 columns
df012 = df012.drop(columns=['WarShortName_s2', 'WarType_s2'])

# Join with s3 on WarID to get IsInternational
df_final = pd.merge(df012, s3[['WarID', 'IsInternational']], on='WarID', how='inner')

# Fill missing IsIntervention with 0 (only s1 has it)
df_final['IsIntervention'] = df_final['IsIntervention'].fillna(0).astype(int)

# Fill missing IsInternational with 0 (only s3 has it)
df_final['IsInternational'] = df_final['IsInternational'].fillna(0).astype(int)

# Cast columns to correct types
df_final['WarID'] = df_final['WarID'].astype(int)
df_final['WarShortName'] = df_final['WarShortName'].astype(str)
df_final['WarType'] = df_final['WarType'].astype(int)

# Select columns in target schema order
final = df_final[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)