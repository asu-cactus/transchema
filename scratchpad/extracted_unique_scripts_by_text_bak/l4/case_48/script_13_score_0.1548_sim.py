import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df_a = df0[['WarNum', 'Initiator', 'Outcome', 'SideADeaths', 'CcodeA', 'SideA',
            'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1']].copy()
df_a.rename(columns={
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
}, inplace=True)
df_a['Initiator'] = df_a['Initiator'].astype(str)
df_a['WarID'] = pd.to_numeric(df_a['WarID'], errors='coerce').astype('Int64')
df_a['PolityID'] = pd.to_numeric(df_a['PolityID'], errors='coerce').astype('Int64')
df_a['PolityName'] = pd.to_numeric(df_a['PolityName'], errors='coerce').astype('Int64')
df_a['StartMonth'] = pd.to_numeric(df_a['StartMonth'], errors='coerce').astype('Int64')
df_a['StartDay'] = pd.to_numeric(df_a['StartDay'], errors='coerce').astype('Int64')
df_a['StartYear'] = pd.to_numeric(df_a['StartYear'], errors='coerce').astype('Int64')
df_a['EndMonth'] = pd.to_numeric(df_a['EndMonth'], errors='coerce').astype('Int64')
df_a['EndDay'] = pd.to_numeric(df_a['EndDay'], errors='coerce').astype('Int64')
df_a['EndYear'] = pd.to_numeric(df_a['EndYear'], errors='coerce').astype('Int64')
df_a['Outcome'] = pd.to_numeric(df_a['Outcome'], errors='coerce').astype('Int64')
df_a['Deaths'] = pd.to_numeric(df_a['Deaths'], errors='coerce').fillna(0).astype('Int64')

df_b = df0[['WarNum', 'Initiator', 'Outcome', 'SideBDeaths', 'CcodeB', 'SideB',
            'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2']].copy()
df_b.rename(columns={
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
}, inplace=True)
df_b['Initiator'] = df_b['Initiator'].astype(str)
df_b['WarID'] = pd.to_numeric(df_b['WarID'], errors='coerce').astype('Int64')
df_b['PolityID'] = pd.to_numeric(df_b['PolityID'], errors='coerce').astype('Int64')
df_b['PolityName'] = pd.to_numeric(df_b['PolityName'], errors='coerce').astype('Int64')
df_b['StartMonth'] = pd.to_numeric(df_b['StartMonth'], errors='coerce').astype('Int64')
df_b['StartDay'] = pd.to_numeric(df_b['StartDay'], errors='coerce').astype('Int64')
df_b['StartYear'] = pd.to_numeric(df_b['StartYear'], errors='coerce').astype('Int64')
df_b['EndMonth'] = pd.to_numeric(df_b['EndMonth'], errors='coerce').astype('Int64')
df_b['EndDay'] = pd.to_numeric(df_b['EndDay'], errors='coerce').astype('Int64')
df_b['EndYear'] = pd.to_numeric(df_b['EndYear'], errors='coerce').astype('Int64')
df_b['Outcome'] = pd.to_numeric(df_b['Outcome'], errors='coerce').astype('Int64')
df_b['Deaths'] = pd.to_numeric(df_b['Deaths'], errors='coerce').fillna(0).astype('Int64')

df_final = pd.concat([df_a, df_b], ignore_index=True)

df_final = df_final[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                     'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)