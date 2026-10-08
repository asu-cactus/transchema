import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df_sideA = df0[['WarNum', 'SideA', 'CcodeA', 'WarName', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
df_sideA.columns = ['WarID', 'PolityName', 'PolityID', 'WarName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

df_sideB = df0[['WarNum', 'SideB', 'CcodeB', 'WarName', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
df_sideB.columns = ['WarID', 'PolityName', 'PolityID', 'WarName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

df = pd.concat([df_sideA, df_sideB], ignore_index=True)

df['PolityName'] = df['PolityName'].astype(str)
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').fillna(0).astype('Int64')
df['Initiator'] = df['Initiator'].astype(str)

group_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome']

df_grouped = df.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

df_grouped = df_grouped[group_cols + ['Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)