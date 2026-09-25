import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df_a = df0[['WarNum', 'WarName', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
df_a.columns = ['WarID', 'PolityName', 'PolityID', 'PolityName2', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

df_b = df0[['WarNum', 'WarName', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
df_b.columns = ['WarID', 'PolityName', 'PolityID', 'PolityName2', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

df_a = df_a.drop(columns=['PolityName2'])
df_b = df_b.drop(columns=['PolityName2'])

df_a['PolityName'] = df_a['PolityName'].astype(str)
df_b['PolityName'] = df_b['PolityName'].astype(str)

df_a['PolityID'] = pd.to_numeric(df_a['PolityID'], errors='coerce').fillna(0).astype(int)
df_b['PolityID'] = pd.to_numeric(df_b['PolityID'], errors='coerce').fillna(0).astype(int)

for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']:
    df_a[col] = pd.to_numeric(df_a[col], errors='coerce').fillna(0).astype(int)
    df_b[col] = pd.to_numeric(df_b[col], errors='coerce').fillna(0).astype(int)

df = pd.concat([df_a, df_b], ignore_index=True)

df = df[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)