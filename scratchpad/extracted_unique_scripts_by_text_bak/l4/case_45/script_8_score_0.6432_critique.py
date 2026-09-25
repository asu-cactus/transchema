import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source4_45_0 and Source4_45_1
union_df = pd.concat([df0, df1], ignore_index=True)

# JOIN union_df with df2 on WarID (left join to keep all wars)
join_1 = pd.merge(union_df, df2[['WarID', 'IsIntervention']], on='WarID', how='left')

# JOIN the above with df3 on WarID
join_2 = pd.merge(join_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# GROUP BY WarType and aggregate counts
agg_df = join_2.groupby('WarType', as_index=False).agg(
    WarID=('WarID', 'count'),
    IsIntervention=('IsIntervention', lambda x: x.notna().sum()),
    IsInternational=('IsInternational', lambda x: x.notna().sum())
)

# WarShortName in target schema is integer type but from examples it seems to be count of WarShortName (same as WarID count)
# So assign WarShortName = WarID count
agg_df['WarShortName'] = agg_df['WarID']

# Reorder columns to match target schema
final_df = agg_df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Ensure integer types with no NaNs
final_df = final_df.fillna(0).astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)