import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1 (same schema)
df01 = pd.concat([df0, df1], ignore_index=True)

# JOIN unioned df01 with df2 on WarID (left join to keep all wars from df01)
df012 = pd.merge(df01, df2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN df012 with df3 on WarID (left join)
df0123 = pd.merge(df012, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# GROUP BY WarType and aggregate counts and max flags
df_target = df0123.groupby('WarType', dropna=False).agg(
    WarID=('WarID', 'nunique'),
    WarShortName=('WarShortName', 'nunique'),
    IsInternational=('IsInternational', 'max'),
    IsIntervention=('IsIntervention', 'max')
).reset_index()

# Ensure correct column order and types
df_target = df_target[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

df_target = df_target.astype({
    'WarType': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'IsInternational': 'Int64',
    'IsIntervention': 'Int64'
})

# Write output
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)