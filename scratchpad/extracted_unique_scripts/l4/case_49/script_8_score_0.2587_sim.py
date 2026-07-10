import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').fillna(0).astype(int)
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').fillna(0).astype(int)
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').fillna(0).astype(int)

grouped = df0.groupby(['WarNum', 'CcodeA'], as_index=False).agg(
    StartYear=('StartYear1', 'min'),
    EndYear=('EndYear1', 'max'),
    SideADeaths=('SideADeaths', 'sum'),
    SideBDeaths=('SideBDeaths', 'sum'),
    WarCount=('WarNum', 'count')
)

grouped['Deaths'] = grouped['SideADeaths'] + grouped['SideBDeaths']

grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'StartYear': 'StartYear',
    'EndYear': 'EndYear'
}, inplace=True)

grouped['PolityName'] = None
grouped['StartMonth'] = 1
grouped['StartDay'] = 1
grouped['EndMonth'] = 1
grouped['EndDay'] = 1
grouped['Initiator'] = None
grouped['Outcome'] = None

cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
        'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

result = grouped[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)