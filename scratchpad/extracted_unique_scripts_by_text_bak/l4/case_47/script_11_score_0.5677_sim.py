import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

df0['IsIntervention'] = 0
df2['IsIntervention'] = 0

union_0 = pd.concat([df0, df2], ignore_index=True)
union_1 = pd.concat([df1, df3], ignore_index=True)

final_df = pd.concat([union_0, union_1], ignore_index=True)

final_df = final_df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final_df['IsIntervention'] = final_df['IsIntervention'].fillna(0).astype(int)
final_df['WarID'] = final_df['WarID'].astype(int)
final_df['WarShortName'] = final_df['WarShortName'].astype(str)
final_df['WarType'] = final_df['WarType'].astype(int)
final_df['IsInternational'] = final_df['IsInternational'].fillna(0).astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)