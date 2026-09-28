import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION Source0 and Source2 (same schema)
union_0_2 = pd.concat([df0, df2], ignore_index=True)

# JOIN union_0_2 with Source1 on WarID (to get IsIntervention)
join_1 = pd.merge(union_0_2, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN join_1 with Source3 on WarID (to get IsInternational)
join_2 = pd.merge(join_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill NaNs in IsIntervention and IsInternational with 0 and convert to int
join_2['IsIntervention'] = join_2['IsIntervention'].fillna(0).astype(int)
join_2['IsInternational'] = join_2['IsInternational'].fillna(0).astype(int)

# Group by WarID, aggregate IsIntervention (max), WarType (first), IsInternational (max)
agg_df = join_2.groupby('WarID', as_index=False).agg({
    'IsIntervention': 'max',
    'WarType': 'first',
    'IsInternational': 'max'
})

# Set WarShortName = WarID (as int)
agg_df['WarShortName'] = agg_df['WarID'].astype(int)

# Reorder columns to match target schema
result = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)