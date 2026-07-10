import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv"
df = pd.read_csv(src0_path, index_col=0)

df_left = df[['WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
df_left.rename(columns={
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
}, inplace=True)
df_left['Initiator'] = df_left['Initiator'].astype('Int64')
df_left['Outcome'] = df_left['Outcome'].astype('Int64')
df_left['Deaths'] = df_left['Deaths'].fillna(0).astype('Int64')
df_left['StartMonth'] = df_left['StartMonth'].fillna(0).astype('Int64')
df_left['StartDay'] = df_left['StartDay'].fillna(0).astype('Int64')
df_left['StartYear'] = df_left['StartYear'].fillna(0).astype('Int64')
df_left['EndMonth'] = df_left['EndMonth'].fillna(0).astype('Int64')
df_left['EndDay'] = df_left['EndDay'].fillna(0).astype('Int64')
df_left['EndYear'] = df_left['EndYear'].fillna(0).astype('Int64')

df_right = df[['WarNum', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
df_right.rename(columns={
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
}, inplace=True)
df_right['Initiator'] = df_right['Initiator'].astype('Int64')
df_right['Outcome'] = df_right['Outcome'].astype('Int64')
df_right['Deaths'] = df_right['Deaths'].fillna(0).astype('Int64')
df_right['StartMonth'] = df_right['StartMonth'].fillna(0).astype('Int64')
df_right['StartDay'] = df_right['StartDay'].fillna(0).astype('Int64')
df_right['StartYear'] = df_right['StartYear'].fillna(0).astype('Int64')
df_right['EndMonth'] = df_right['EndMonth'].fillna(0).astype('Int64')
df_right['EndDay'] = df_right['EndDay'].fillna(0).astype('Int64')
df_right['EndYear'] = df_right['EndYear'].fillna(0).astype('Int64')

df_all = pd.concat([df_left, df_right], ignore_index=True)
df_all = df_all.dropna(subset=['PolityName'])

df_all['WarID'] = df_all['WarNum'].astype('Int64')
df_all = df_all.drop(columns=['WarNum'])

df_all = df_all[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)