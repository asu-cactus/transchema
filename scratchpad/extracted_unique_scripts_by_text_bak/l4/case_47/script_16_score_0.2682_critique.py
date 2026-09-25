import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Prepare s1 subset for union (only columns matching s0 and s2)
s1_subset = s1[['WarID', 'WarShortName', 'WarType']]

# UNION s0, s1_subset, s2
union_df = pd.concat([s0, s1_subset, s2], ignore_index=True)

# Join union_df with s1 to get IsIntervention
join1 = pd.merge(union_df, s1[['WarID', 'IsIntervention']], on='WarID', how='left')

# Join with s3 to get IsInternational
join2 = pd.merge(join1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Group by WarID and aggregate
agg_df = join2.groupby('WarID', as_index=False).agg({
    'IsIntervention': 'max',
    'IsInternational': 'max',
    'WarShortName': 'first',
    'WarType': 'first'
})

# Reorder columns to match target schema
final = agg_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Ensure correct dtypes
final['IsIntervention'] = final['IsIntervention'].astype('Int64')
final['WarID'] = final['WarID'].astype('Int64')
final['WarShortName'] = final['WarShortName'].astype(str)
final['WarType'] = final['WarType'].astype('Int64')
final['IsInternational'] = final['IsInternational'].astype('Int64')

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)