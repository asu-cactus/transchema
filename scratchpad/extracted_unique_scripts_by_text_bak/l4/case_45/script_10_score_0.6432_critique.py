import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1 (same schema)
df01 = pd.concat([df0, df1], ignore_index=True)

# JOIN unioned df01 with df2 on WarID (left join to keep all wars)
df_join_2 = pd.merge(df01, df2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN the above with df3 on WarID
df_join_3 = pd.merge(df_join_2, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill NaN in flags with 0
df_join_3['IsIntervention'] = df_join_3['IsIntervention'].fillna(0).astype(int)
df_join_3['IsInternational'] = df_join_3['IsInternational'].fillna(0).astype(int)

# GROUP BY WarType
agg_df = df_join_3.groupby('WarType', as_index=False).agg({
    'WarID': 'count',            # count of WarID per WarType
    'WarShortName': 'count',     # count of WarShortName per WarType (same as WarID count)
    'IsInternational': 'sum',    # sum of IsInternational flags
    'IsIntervention': 'sum'      # sum of IsIntervention flags
})

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'WarID': 'WarID',
    'WarShortName': 'WarShortName',
    'IsInternational': 'IsInternational',
    'IsIntervention': 'IsIntervention'
})

# Ensure correct dtypes
agg_df['WarType'] = agg_df['WarType'].astype(int)
agg_df['WarID'] = agg_df['WarID'].astype(int)
agg_df['WarShortName'] = agg_df['WarShortName'].astype(int)
agg_df['IsInternational'] = agg_df['IsInternational'].astype(int)
agg_df['IsIntervention'] = agg_df['IsIntervention'].astype(int)

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)