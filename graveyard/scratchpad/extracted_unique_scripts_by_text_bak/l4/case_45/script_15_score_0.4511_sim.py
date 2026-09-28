import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

df01 = pd.concat([df0, df1], ignore_index=True)

pivot = df01.pivot(index='WarID', columns='WarType', values='WarID')
pivot = pivot.fillna(0).astype(int).reset_index()

pivot_cols = [col for col in pivot.columns if col != 'WarID']
pivot = pivot.rename(columns={col: int(col) for col in pivot_cols})

pivot_long = pivot.melt(id_vars='WarID', var_name='WarType', value_name='WarID_val')
pivot_long = pivot_long[pivot_long['WarID_val'] != 0].drop(columns='WarID_val')

pivot_long = pivot_long.astype({'WarType': int, 'WarID': int})

df2_sub = df2[['WarID', 'IsIntervention']].copy()
df3_sub = df3[['WarID', 'IsInternational']].copy()

join1 = pd.merge(pivot_long, df2_sub, on='WarID', how='left')
join2 = pd.merge(join1, df3_sub, on='WarID', how='left')

warshort = pd.concat([df0[['WarID', 'WarShortName']], df1[['WarID', 'WarShortName']], df2[['WarID', 'WarShortName']], df3[['WarID', 'WarShortName']]], ignore_index=True)
warshort = warshort.drop_duplicates(subset='WarID')

result = pd.merge(join2, warshort, on='WarID', how='left')

result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

result['WarType'] = result['WarType'].astype(int)
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].apply(lambda x: int(x) if str(x).isdigit() else 0)
result['IsInternational'] = result['IsInternational'].fillna(0).astype(int)
result['IsIntervention'] = result['IsIntervention'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)