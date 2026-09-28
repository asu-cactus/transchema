import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0)
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce')
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce')

agg = df0.groupby(['WarNum', 'CcodeA', 'WarName'], dropna=False).agg(
    StartYear=('StartYear1', 'min'),
    EndYear=('EndYear1', 'max'),
    SideADeaths=('SideADeaths', 'sum'),
    SideBDeaths=('SideBDeaths', 'sum'),
    WarTypeCount=('WarType', 'count')
).reset_index()

agg['Deaths'] = agg['SideADeaths'] + agg['SideBDeaths']

agg['PolityName'] = agg['WarName'].astype(str)
agg['WarID'] = agg['WarNum'].astype('Int64')
agg['PolityID'] = agg['CcodeA'].astype('Int64')

agg['StartMonth'] = 1
agg['StartDay'] = 1
agg['EndMonth'] = 1
agg['EndDay'] = 1

agg['Initiator'] = agg['WarID']
agg['Outcome'] = agg['WarID']

result = agg[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)