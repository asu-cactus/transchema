import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION Source0 and Source2 (same schema)
union_0_2 = pd.concat([source0, source2], ignore_index=True)

# JOIN union_0_2 with source1 on WarID (left join to keep all wars)
join_01 = pd.merge(union_0_2, source1[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN the above with source3 on WarID (left join)
join_012 = pd.merge(join_01, source3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsInternational and IsIntervention with 0
join_012['IsInternational'] = join_012['IsInternational'].fillna(0).astype(int)
join_012['IsIntervention'] = join_012['IsIntervention'].fillna(0).astype(int)

# Group by WarID (unique key), aggregate other columns by first occurrence
final_df = join_012.groupby('WarID', as_index=False).agg({
    'IsInternational': 'first',
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'first'
})

# Reorder columns to match target schema
final_df = final_df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

# Ensure correct dtypes
final_df['IsInternational'] = final_df['IsInternational'].astype(int)
final_df['WarID'] = final_df['WarID'].astype(int)
final_df['WarShortName'] = final_df['WarShortName'].astype(str)
final_df['WarType'] = final_df['WarType'].astype(int)
final_df['IsIntervention'] = final_df['IsIntervention'].astype(int)

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)