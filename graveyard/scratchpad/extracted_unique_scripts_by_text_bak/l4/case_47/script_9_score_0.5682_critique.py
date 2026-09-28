import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Union all three tables with same schema (dropping IsIntervention from df1 to match others)
df1_subset = df1[['WarID', 'WarShortName', 'WarType']]
union_source = pd.concat([df0, df1_subset, df2], ignore_index=True)

# Join union_source with df1 to get IsIntervention
joined_1 = pd.merge(union_source, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

# Join with df3 to get IsInternational
joined_2 = pd.merge(joined_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsIntervention and IsInternational with 0
joined_2['IsIntervention'] = joined_2['IsIntervention'].fillna(0).astype(int)
joined_2['IsInternational'] = joined_2['IsInternational'].fillna(0).astype(int)

# Map WarShortName strings to integers by mapping unique strings to unique integers
warshortname_map = {v: k for k, v in enumerate(joined_2['WarShortName'].unique(), start=1)}
joined_2['WarShortName'] = joined_2['WarShortName'].map(warshortname_map).astype(int)

# Cast other columns to int as per target schema
joined_2['WarID'] = joined_2['WarID'].astype(int)
joined_2['WarType'] = joined_2['WarType'].astype(int)

# Drop duplicates to match unique WarID rows (target examples have unique WarID)
result = joined_2.drop_duplicates(subset=['WarID'])

# Select columns in target schema order
result = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)