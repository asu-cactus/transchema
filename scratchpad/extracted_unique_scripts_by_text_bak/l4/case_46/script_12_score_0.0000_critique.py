import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION df0 and df2 (same schema)
union_result = pd.concat([df0, df2], ignore_index=True)

# JOIN union_result with df1 on WarID (inner join to keep only matching WarIDs)
join_result_1 = pd.merge(union_result, df1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN join_result_1 with df3 on WarID (inner join)
join_result_2 = pd.merge(join_result_1, df3[['WarID', 'IsInternational']], on='WarID', how='inner')

# GROUP BY WarID, aggregate other columns by first
agg_df = join_result_2.groupby('WarID', as_index=False).agg({
    'IsInternational': 'first',
    'WarShortName': 'first',
    'WarType': 'first',
    'IsIntervention': 'first'
})

# Reorder columns to match target schema
result = agg_df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)