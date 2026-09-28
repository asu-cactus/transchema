import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source4_45_0 and Source4_45_1
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_0_1 with Source4_45_2 on WarID (left join to keep all WarIDs)
join_0_1_2 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN the above with Source4_45_3 on WarID (left join)
join_0_1_2_3 = pd.merge(join_0_1_2, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Replace NaN in IsInternational and IsIntervention with 0 (as per hint 24)
join_0_1_2_3['IsInternational'] = join_0_1_2_3['IsInternational'].fillna(0).astype(int)
join_0_1_2_3['IsIntervention'] = join_0_1_2_3['IsIntervention'].fillna(0).astype(int)

# GROUP BY WarType and aggregate counts and sums
final = join_0_1_2_3.groupby('WarType', as_index=False).agg({
    'WarID': 'count',           # count of WarID per WarType
    'WarShortName': 'count',    # count of WarShortName per WarType
    'IsInternational': 'sum',   # sum of IsInternational per WarType
    'IsIntervention': 'sum'     # sum of IsIntervention per WarType
})

# Rename columns to match target schema exactly
final = final.rename(columns={
    'WarID': 'WarID',
    'WarShortName': 'WarShortName',
    'IsInternational': 'IsInternational',
    'IsIntervention': 'IsIntervention',
    'WarType': 'WarType'
})

# Reorder columns to match target schema: ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']
final = final[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)