import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df_a = df0[['WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']]
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
df_a['PolityName'] = pd.to_numeric(df_a['PolityName'], errors='coerce').astype('Int64')

df_b = df0[['WarNum', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']]
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
df_b['PolityName'] = pd.to_numeric(df_b['PolityName'], errors='coerce').astype('Int64')

df = pd.concat([df_a, df_b], ignore_index=True)

df = df[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

for col in ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)