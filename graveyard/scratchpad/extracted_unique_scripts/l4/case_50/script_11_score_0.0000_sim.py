import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').astype('Int64')
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').astype('Int64')

agg = df0.groupby(['WarNum', 'CcodeA', 'Initiator'], dropna=False).agg(
    StartYear=('StartYear1', 'min'),
    EndYear=('EndYear1', 'max'),
    SideADeaths=('SideADeaths', 'sum'),
    SideBDeaths=('SideBDeaths', 'sum'),
    WarCount=('WarNum', 'count')
).reset_index()

agg['Deaths'] = agg['SideADeaths'] + agg['SideBDeaths']

agg['Outcome'] = 0
agg['PolityID'] = agg['CcodeA'].astype('Int64')
agg['PolityName'] = agg['CcodeA'].astype('Int64')
agg['WarID'] = agg['WarNum'].astype('Int64')
agg['StartMonth'] = 0
agg['StartDay'] = 0
agg['EndMonth'] = 0
agg['EndDay'] = 0
agg['Initiator'] = agg['Initiator'].astype('Int64')

target = agg[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)