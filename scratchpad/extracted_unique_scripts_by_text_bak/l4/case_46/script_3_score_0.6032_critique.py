import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION Source0 and Source2 (same schema)
union_result = pd.concat([s0, s2], ignore_index=True)

# JOIN union_result with Source3 on WarID (adds IsInternational)
join1 = pd.merge(union_result, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# JOIN the above with Source1 on WarID (adds IsIntervention)
join2 = pd.merge(join1, s1[['WarID', 'IsIntervention']], on='WarID', how='left')

# Fill NaNs in IsInternational and IsIntervention with 0 and convert to int
join2['IsInternational'] = join2['IsInternational'].fillna(0).astype(int)
join2['IsIntervention'] = join2['IsIntervention'].fillna(0).astype(int)

# Group by IsInternational and WarID (leftmost unique columns)
# Aggregate WarShortName and WarType by first (string and int respectively)
# Aggregate IsIntervention by max (flag)
agg_df = join2.groupby(['IsInternational', 'WarID'], as_index=False).agg({
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'max'
})

# Ensure correct types
agg_df['WarShortName'] = agg_df['WarShortName'].astype(str)
agg_df['WarType'] = agg_df['WarType'].astype(int)
agg_df['IsInternational'] = agg_df['IsInternational'].astype(int)
agg_df['WarID'] = agg_df['WarID'].astype(int)
agg_df['IsIntervention'] = agg_df['IsIntervention'].astype(int)

# Reorder columns to match target schema
final = agg_df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)