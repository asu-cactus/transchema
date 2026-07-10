import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df0['Outcome'] = pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64')
df0['WarNum'] = pd.to_numeric(df0['WarNum'], errors='coerce').astype('Int64')
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').astype('Int64')
df0['Initiator'] = pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64')
df0['StartMonth1'] = pd.to_numeric(df0['StartMonth1'], errors='coerce').astype('Int64')
df0['StartDay1'] = pd.to_numeric(df0['StartDay1'], errors='coerce').astype('Int64')
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').astype('Int64')
df0['EndMonth1'] = pd.to_numeric(df0['EndMonth1'], errors='coerce').astype('Int64')
df0['EndDay1'] = pd.to_numeric(df0['EndDay1'], errors='coerce').astype('Int64')
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').astype('Int64')
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)

df_grouped = df0.groupby(
    ['Outcome', 'WarNum', 'CcodeA', 'Initiator', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1'],
    dropna=False,
    as_index=False
).agg({'SideADeaths': 'sum', 'SideBDeaths': 'sum'})

df_grouped['Deaths'] = df_grouped['SideADeaths'] + df_grouped['SideBDeaths']

df_grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'Initiator': 'Initiator',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
}, inplace=True)

df_grouped['PolityName'] = df_grouped['PolityID']

df_final = df_grouped[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

df_final = df_final.astype({
    'Outcome': 'Int64',
    'WarID': 'Int64',
    'PolityID': 'Int64',
    'PolityName': 'Int64',
    'StartMonth': 'Int64',
    'StartDay': 'Int64',
    'StartYear': 'Int64',
    'EndMonth': 'Int64',
    'EndDay': 'Int64',
    'EndYear': 'Int64',
    'Initiator': 'Int64',
    'Deaths': 'Int64'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)