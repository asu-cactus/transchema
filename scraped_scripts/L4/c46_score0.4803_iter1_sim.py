import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

pivot_df3 = df3[['WarID', 'IsInternational']]

union_df = pd.concat([df0, df1, df2], ignore_index=True, sort=False)

merged = pd.merge(union_df, pivot_df3, on='WarID', how='left')

merged['IsInternational'] = merged['IsInternational'].fillna(0).astype(int)
merged['IsIntervention'] = merged['IsIntervention'].fillna(0).astype(int)
merged['WarID'] = merged['WarID'].astype(int)
merged['WarShortName'] = merged['WarShortName'].astype(str)
merged['WarType'] = merged['WarType'].astype(int)

result = merged[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)