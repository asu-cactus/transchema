import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION Source4_46_0 and Source4_46_2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# JOIN union_0_2 with Source4_46_1 on WarID (inner join to avoid unmatched rows)
joined_0_1 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on="WarID", how="inner")

# JOIN the above with Source4_46_3 on WarID (inner join)
joined_all = pd.merge(joined_0_1, s3[['WarID', 'IsInternational']], on="WarID", how="inner")

# GROUP BY WarID and aggregate
# For WarShortName and WarType, take first (assuming unique per WarID)
# For IsIntervention and IsInternational, take max (binary flags)
agg_df = joined_all.groupby('WarID', as_index=False).agg({
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'max',
    'IsInternational': 'max'
})

# Reorder columns to match target schema: ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']
final = agg_df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Ensure correct types
final['IsInternational'] = final['IsInternational'].astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype(int)
final['IsIntervention'] = final['IsIntervention'].astype(int)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)