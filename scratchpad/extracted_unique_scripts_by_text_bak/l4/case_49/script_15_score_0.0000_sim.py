import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df_out = pd.DataFrame()
df_out['PolityName'] = df['SideA'].fillna('') + df['SideB'].fillna('')
df_out['WarID'] = df['WarNum'].astype('Int64')
df_out['PolityID'] = 0
df_out['StartMonth'] = df['StartMonth1'].fillna(1).astype('Int64')
df_out['StartDay'] = df['StartDay1'].fillna(1).astype('Int64')
df_out['StartYear'] = df['StartYear1'].fillna(1).astype('Int64')
df_out['EndMonth'] = df['EndMonth1'].fillna(1).astype('Int64')
df_out['EndDay'] = df['EndDay1'].fillna(1).astype('Int64')
df_out['EndYear'] = df['EndYear1'].fillna(1).astype('Int64')
df_out['Initiator'] = df['Initiator'].astype('Int64')
df_out['Outcome'] = df['Outcome'].astype('Int64')
df_out['Deaths'] = df['SideADeaths'].fillna(0).astype('Int64') + df['SideBDeaths'].fillna(0).astype('Int64')

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)