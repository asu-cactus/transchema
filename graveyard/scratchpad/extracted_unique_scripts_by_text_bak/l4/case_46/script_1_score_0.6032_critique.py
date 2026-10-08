import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# Add missing columns with default values for union of df0 and df2
df0['IsIntervention'] = 0
df0['IsInternational'] = 0

df2['IsIntervention'] = 0
df2['IsInternational'] = 0

# Union df0 and df2
df_union_0_2 = pd.concat([df0, df2], ignore_index=True)

# Add missing columns to df1 and df3 for consistent join
df1['IsInternational'] = 0
df3['IsIntervention'] = 0

# Join union_0_2 with df1 on WarID (inner join to keep only matching WarIDs)
df_join_1 = pd.merge(df_union_0_2, df1[['WarID', 'IsIntervention']], on='WarID', how='left', suffixes=('', '_df1'))
# For rows where IsIntervention is missing (NaN), fill with 0
df_join_1['IsIntervention'] = df_join_1['IsIntervention'].fillna(0).astype(int)

# Join the above with df3 on WarID to get IsInternational
df_join_2 = pd.merge(df_join_1, df3[['WarID', 'IsInternational']], on='WarID', how='left', suffixes=('', '_df3'))
df_join_2['IsInternational'] = df_join_2['IsInternational'].fillna(0).astype(int)

# Ensure correct types
df_join_2['WarID'] = df_join_2['WarID'].astype(int)
df_join_2['WarShortName'] = df_join_2['WarShortName'].astype(str)
df_join_2['WarType'] = df_join_2['WarType'].astype(int)
df_join_2['IsIntervention'] = df_join_2['IsIntervention'].astype(int)
df_join_2['IsInternational'] = df_join_2['IsInternational'].astype(int)

# Select columns in target order
df_result = df_join_2[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)