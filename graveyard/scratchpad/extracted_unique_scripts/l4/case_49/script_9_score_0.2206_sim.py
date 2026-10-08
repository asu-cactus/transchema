import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df_a = df[['WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths']].copy()
df_a.columns = ['WarNum', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Deaths']
df_a['Initiator'] = df['Initiator']
df_a['Outcome'] = df['Outcome']

df_b = df[['WarNum', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'SideBDeaths']].copy()
df_b.columns = ['WarNum', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Deaths']
df_b['Initiator'] = df['Initiator']
df_b['Outcome'] = df['Outcome']

df_long = pd.concat([df_a, df_b], ignore_index=True)

df_long['WarID'] = df_long['WarNum'].astype('Int64')
df_long['PolityID'] = pd.to_numeric(df_long['PolityID'], errors='coerce').astype('Int64')
df_long['StartMonth'] = pd.to_numeric(df_long['StartMonth'], errors='coerce').astype('Int64')
df_long['StartDay'] = pd.to_numeric(df_long['StartDay'], errors='coerce').astype('Int64')
df_long['StartYear'] = pd.to_numeric(df_long['StartYear'], errors='coerce').astype('Int64')
df_long['EndMonth'] = pd.to_numeric(df_long['EndMonth'], errors='coerce').astype('Int64')
df_long['EndDay'] = pd.to_numeric(df_long['EndDay'], errors='coerce').astype('Int64')
df_long['EndYear'] = pd.to_numeric(df_long['EndYear'], errors='coerce').astype('Int64')
df_long['Initiator'] = pd.to_numeric(df_long['Initiator'], errors='coerce').astype('Int64')
df_long['Outcome'] = pd.to_numeric(df_long['Outcome'], errors='coerce').astype('Int64')
df_long['Deaths'] = pd.to_numeric(df_long['Deaths'], errors='coerce').astype('Int64')

df_long = df_long.drop(columns=['WarNum'])

df_final = df_long.groupby(['PolityName', 'WarID'], as_index=False).agg({
    'PolityID': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'StartYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'EndYear': 'first',
    'Initiator': 'first',
    'Outcome': 'first',
    'Deaths': 'sum'
})

df_final = df_final[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)