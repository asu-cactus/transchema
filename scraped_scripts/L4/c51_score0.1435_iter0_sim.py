import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

df1['PolityName'] = pd.NA

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

df_all['PolityName'] = pd.to_numeric(df_all['PolityName'], errors='coerce')

df_all['Side'] = df_all['Side'].astype(str)
df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')
df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').astype('Int64')
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').astype('Int64')

df_all = df_all[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)