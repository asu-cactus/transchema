import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df_long_a = df[['WarNum', 'Initiator', 'Outcome', 'SideA', 'CcodeA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths']].copy()
df_long_a = df_long_a.rename(columns={
    'SideA': 'PolityName',
    'CcodeA': 'PolityID',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})
df_long_a['Initiator'] = df_long_a['Initiator'].astype(str)
df_long_a['PolityName'] = df_long_a['PolityName'].astype(str)

df_long_b = df[['WarNum', 'Initiator', 'Outcome', 'SideB', 'CcodeB', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideBDeaths']].copy()
df_long_b = df_long_b.rename(columns={
    'SideB': 'PolityName',
    'CcodeB': 'PolityID',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideBDeaths': 'Deaths'
})
df_long_b['Initiator'] = df_long_b['Initiator'].astype(str)
df_long_b['PolityName'] = df_long_b['PolityName'].astype(str)

df_long = pd.concat([df_long_a, df_long_b], ignore_index=True)

df_long = df_long.dropna(subset=['PolityID'])

df_long['WarID'] = df_long['WarNum'].astype(int)
df_long['PolityID'] = df_long['PolityID'].astype(int)
df_long['PolityName'] = df_long['PolityName'].apply(lambda x: x if x != 'nan' else None)

for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']:
    df_long[col] = pd.to_numeric(df_long[col], errors='coerce').fillna(0).astype(int)

df_long = df_long.rename(columns={'Initiator': 'Initiator'})

result = df_long[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)