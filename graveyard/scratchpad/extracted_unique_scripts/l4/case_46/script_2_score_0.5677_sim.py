import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

df0['IsInternational'] = 0
df2['IsInternational'] = 0

df_union_0_2 = pd.concat([df0, df2], ignore_index=True)

df1['IsInternational'] = 0

df_all = pd.concat([df_union_0_2, df1, df3], ignore_index=True)

df_all['IsIntervention'] = df_all['IsIntervention'].fillna(0).astype(int)
df_all['IsInternational'] = df_all['IsInternational'].astype(int)
df_all['WarID'] = df_all['WarID'].astype(int)
df_all['WarShortName'] = df_all['WarShortName'].astype(str)
df_all['WarType'] = df_all['WarType'].astype(int)

df_all['WarShortName'] = pd.to_numeric(df_all['WarShortName'], errors='coerce').fillna(0).astype(int)

df_all = df_all[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)