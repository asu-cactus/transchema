import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)

join_1 = pd.merge(union_df, df2[['WarID', 'IsIntervention']], on='WarID', how='left')

final_df = pd.merge(join_1, df3[['WarID', 'IsInternational']], on='WarID', how='left')

final_df = final_df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

final_df['WarType'] = final_df['WarType'].astype('Int64')
final_df['WarID'] = final_df['WarID'].astype('Int64')
final_df['WarShortName'] = final_df['WarShortName'].astype('Int64', errors='ignore') if final_df['WarShortName'].dtype != 'Int64' else final_df['WarShortName']
final_df['IsInternational'] = final_df['IsInternational'].fillna(0).astype('Int64')
final_df['IsIntervention'] = final_df['IsIntervention'].fillna(0).astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)