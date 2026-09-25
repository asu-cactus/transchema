import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df_a = df[['WarNum', 'Initiator', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Outcome', 'SideADeaths']]
df_b = df[['WarNum', 'Initiator', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Outcome', 'SideBDeaths']]

df_a = df_a.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

df_b = df_b.rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
})

df_all = pd.concat([df_a, df_b], ignore_index=True)

df_all = df_all.dropna(subset=['PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear'])

df_all['PolityID'] = df_all['PolityID'].astype(int)
df_all['PolityName'] = df_all['PolityName'].astype(str)
df_all['StartMonth'] = df_all['StartMonth'].astype(int)
df_all['StartDay'] = df_all['StartDay'].astype(int)
df_all['StartYear'] = df_all['StartYear'].astype(int)
df_all['EndMonth'] = df_all['EndMonth'].astype(int)
df_all['EndDay'] = df_all['EndDay'].astype(int)
df_all['EndYear'] = df_all['EndYear'].astype(int)
df_all['Outcome'] = df_all['Outcome'].astype(int)
df_all['Deaths'] = df_all['Deaths'].fillna(0).astype(int)
df_all['WarID'] = df_all['WarID'].astype(int)
df_all['Initiator'] = df_all['Initiator'].astype(str)

result = df_all[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)