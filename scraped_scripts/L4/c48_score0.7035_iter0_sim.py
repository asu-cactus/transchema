import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df = df0.copy()

df['Initiator'] = df['Initiator'].astype(str)

df_grouped = df.groupby('Initiator', as_index=False).agg({
    'WarNum': 'first',
    'CcodeA': 'first',
    'SideA': 'first',
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'StartYear1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'EndYear1': 'first',
    'Outcome': 'first',
    'SideADeaths': 'first'
})

df_grouped.rename(columns={
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

for col in ['WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']:
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').fillna(0).astype(int)

df_grouped = df_grouped[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)