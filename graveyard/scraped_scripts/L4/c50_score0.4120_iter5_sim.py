import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').fillna(0).astype(int)
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').fillna(0).astype(int)
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').fillna(0).astype(int)

agg = df0.groupby(['WarNum', 'CcodeA', 'Initiator'], as_index=False).agg({
    'StartYear1': 'min',
    'EndYear1': 'max',
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum',
    'Outcome': 'first',
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'WarName': 'first'
})

agg['Deaths'] = agg['SideADeaths'] + agg['SideBDeaths']
agg.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'WarName': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear'
}, inplace=True)

agg = agg[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

for col in ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    agg[col] = pd.to_numeric(agg[col], errors='coerce').fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)