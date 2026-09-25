import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Add missing columns with default 0
df0['IsIntervention'] = 0
df0['IsInternational'] = 0

df1['IsInternational'] = 0  # df1 has IsIntervention but no IsInternational

df2['IsIntervention'] = 0
df2['IsInternational'] = 0

# df3 has IsInternational but no IsIntervention
df3['IsIntervention'] = 0

# Join all on WarID
df01 = pd.merge(df0, df1, on='WarID', how='inner', suffixes=('_0', '_1'))
df012 = pd.merge(df01, df2, on='WarID', how='inner', suffixes=('', '_2'))
df0123 = pd.merge(df012, df3, on='WarID', how='inner', suffixes=('', '_3'))

# Select columns for final output:
# For WarShortName and WarType, pick one consistent column (e.g., from df0 or df1)
# Since suffixes added, columns are like WarShortName_0, WarShortName_1, WarShortName, WarShortName_3
# Use WarShortName_0 (from df0) as representative
# Similarly for WarType, use WarType_0

# For IsIntervention and IsInternational, take max across columns to combine flags
# Columns: IsIntervention_0, IsIntervention_1, IsIntervention_2, IsIntervention_3
# Columns: IsInternational_0, IsInternational_1, IsInternational_2, IsInternational_3

# Prepare dataframe for aggregation
agg_df = df0123.copy()

# Rename columns for clarity
agg_df.rename(columns={
    'WarShortName_0': 'WarShortName',
    'WarType_0': 'WarType',
    'IsIntervention_0': 'IsIntervention_0',
    'IsIntervention_1': 'IsIntervention_1',
    'IsIntervention_2': 'IsIntervention_2',
    'IsIntervention_3': 'IsIntervention_3',
    'IsInternational_0': 'IsInternational_0',
    'IsInternational_1': 'IsInternational_1',
    'IsInternational_2': 'IsInternational_2',
    'IsInternational_3': 'IsInternational_3',
}, inplace=True)

# Aggregate IsIntervention and IsInternational by max (since they are flags)
agg_df['IsIntervention'] = agg_df[['IsIntervention_0', 'IsIntervention_1', 'IsIntervention_2', 'IsIntervention_3']].max(axis=1)
agg_df['IsInternational'] = agg_df[['IsInternational_0', 'IsInternational_1', 'IsInternational_2', 'IsInternational_3']].max(axis=1)

# Group by WarID to ensure uniqueness, aggregate other columns by max (since they should be consistent)
final_df = agg_df.groupby('WarID', as_index=False).agg({
    'IsIntervention': 'max',
    'WarShortName': 'max',
    'WarType': 'max',
    'IsInternational': 'max'
})

# Reorder columns to match target schema
final_df = final_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Ensure correct types
final_df['IsIntervention'] = final_df['IsIntervention'].astype(int)
final_df['WarID'] = final_df['WarID'].astype(int)
final_df['WarShortName'] = final_df['WarShortName'].astype(str)
final_df['WarType'] = final_df['WarType'].astype(int)
final_df['IsInternational'] = final_df['IsInternational'].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)