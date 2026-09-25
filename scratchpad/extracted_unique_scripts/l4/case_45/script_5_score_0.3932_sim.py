import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

df01 = pd.concat([df0, df1], ignore_index=True)

df012 = pd.merge(df01, df2[['WarID', 'IsIntervention']], on='WarID', how='left')

df_final = pd.merge(df012, df3[['WarID', 'IsInternational']], on='WarID', how='left')

df_final = df_final[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

df_final['WarType'] = df_final['WarType'].astype('Int64')
df_final['WarID'] = df_final['WarID'].astype('Int64')
df_final['WarShortName'] = df_final['WarShortName'].astype('Int64', errors='ignore')  # WarShortName is string, convert to int not possible, keep as is
# But target schema says WarShortName is integer, so we must convert WarShortName to integer by counting distinct WarShortName per WarType

# Since WarShortName is string, but target schema expects integer, we interpret the partial plan:
# The partial plan says: GROUP_BY WarType with COUNT_DISTINCT WarID and COUNT_DISTINCT WarShortName
# So we need to aggregate counts per WarType for WarID and WarShortName, but target schema expects WarID and WarShortName as integer columns, not counts.

# However, target examples show WarID and WarShortName columns with integer values equal to counts (e.g. WarID=61, WarShortName=61 for WarType=8)
# So we must aggregate counts per WarType for WarID and WarShortName, and fill IsInternational and IsIntervention accordingly.

# So redo aggregation:

agg0 = pd.concat([df0, df1], ignore_index=True)
agg_counts = agg0.groupby('WarType').agg(
    WarID=('WarID', 'nunique'),
    WarShortName=('WarShortName', 'nunique')
).reset_index()

# For IsInternational and IsIntervention, from df3 and df2 respectively, we take max per WarType (since target examples show values per WarType)
is_international = df3.groupby('WarType')['IsInternational'].max().reset_index()
is_intervention = df2.groupby('WarType')['IsIntervention'].max().reset_index()

df_target = agg_counts.merge(is_international, on='WarType', how='left').merge(is_intervention, on='WarType', how='left')

df_target = df_target[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

df_target = df_target.astype({
    'WarType': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'IsInternational': 'Int64',
    'IsIntervention': 'Int64'
})

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)