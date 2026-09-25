import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION Source4_47_0 and Source4_47_2 (same schema)
union_0_2 = pd.concat([source0, source2], ignore_index=True)

# JOIN union_0_2 with Source4_47_1 on WarID
join_01 = pd.merge(union_0_2, source1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN join_01 with Source4_47_3 on WarID
join_all = pd.merge(join_01, source3[['WarID', 'IsInternational']], on='WarID', how='inner')

# GROUP BY IsIntervention and WarID (no aggregation needed, just drop duplicates)
result = join_all.drop_duplicates(subset=['IsIntervention', 'WarID'])

# Project columns in target schema order
result = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Ensure correct dtypes (integer)
result = result.astype({
    'IsIntervention': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'WarType': 'Int64',
    'IsInternational': 'Int64'
}, errors='ignore')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)