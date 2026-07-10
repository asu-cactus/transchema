import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION s0 and s1 (same schema)
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# JOIN union_0_1 with s2 on WarID to get IsIntervention
join_0_1_2 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN the above with s3 on WarID to get IsInternational
join_0_1_2_3 = pd.merge(join_0_1_2, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Group by WarType and aggregate counts and sums
final = join_0_1_2_3.groupby('WarType', as_index=False).agg({
    'WarID': 'count',            # count of WarID per WarType
    'WarShortName': 'count',     # count of WarShortName per WarType (should be same as WarID)
    'IsInternational': 'sum',    # sum of IsInternational flags per WarType
    'IsIntervention': 'sum'      # sum of IsIntervention flags per WarType
})

# Reorder columns to match target schema
final = final[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)