import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# Add missing columns to df0 and df2 to match df1 schema for union
df0['IsIntervention'] = 0  # no info, fill with 0
df0['IsInternational'] = pd.NA  # will be joined later

df2['IsIntervention'] = 0
df2['IsInternational'] = pd.NA

# df1 has IsIntervention, but no IsInternational
df1['IsInternational'] = pd.NA

# Select columns in same order for union
union_cols = ['WarID', 'WarShortName', 'WarType', 'IsIntervention', 'IsInternational']

df0 = df0[union_cols]
df1 = df1[union_cols]
df2 = df2[union_cols]

# Union the three tables
unioned = pd.concat([df0, df1, df2], ignore_index=True)

# Join unioned with df3 on WarID to get IsInternational
# df3 has IsInternational, but no IsIntervention
df3_subset = df3[['WarID', 'IsInternational']]

joined = pd.merge(unioned, df3_subset, on='WarID', how='inner', suffixes=('', '_df3'))

# After join, use IsInternational from df3 (IsInternational_df3)
joined['IsInternational'] = joined['IsInternational_df3']

# Drop the extra IsInternational_df3 column
joined = joined.drop(columns=['IsInternational_df3'])

# Now group by IsInternational and WarID
# For WarShortName, target expects integer matching WarID, so set WarShortName = WarID
joined['WarShortName'] = joined['WarID']

# Aggregate WarType and IsIntervention by max
result = joined.groupby(['IsInternational', 'WarID'], as_index=False).agg({
    'WarShortName': 'first',  # all equal to WarID
    'WarType': 'max',
    'IsIntervention': 'max'
})

# Ensure correct dtypes
result['IsInternational'] = result['IsInternational'].astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(int)
result['WarType'] = result['WarType'].astype(int)
result['IsIntervention'] = result['IsIntervention'].astype(int)

# Reorder columns to match target schema
result = result[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)