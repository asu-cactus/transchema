import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Convert relevant columns to numeric with proper handling
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)
df0['StartMonth1'] = pd.to_numeric(df0['StartMonth1'], errors='coerce').astype('Int64')
df0['StartDay1'] = pd.to_numeric(df0['StartDay1'], errors='coerce').astype('Int64')
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').astype('Int64')
df0['EndMonth1'] = pd.to_numeric(df0['EndMonth1'], errors='coerce').astype('Int64')
df0['EndDay1'] = pd.to_numeric(df0['EndDay1'], errors='coerce').astype('Int64')
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').astype('Int64')
df0['Outcome'] = pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64')
df0['WarNum'] = pd.to_numeric(df0['WarNum'], errors='coerce').astype('Int64')
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').astype('Int64')
df0['Initiator'] = pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64')

agg = df0.groupby(['Outcome', 'WarNum', 'CcodeA'], dropna=False).agg(
    StartMonth=('StartMonth1', 'min'),
    StartDay=('StartDay1', 'min'),
    StartYear=('StartYear1', 'min'),
    EndMonth=('EndMonth1', 'max'),
    EndDay=('EndDay1', 'max'),
    EndYear=('EndYear1', 'max'),
    Initiator=('Initiator', 'min'),
    SideADeaths=('SideADeaths', 'sum'),
    SideBDeaths=('SideBDeaths', 'sum')
).reset_index()

agg['Deaths'] = agg['SideADeaths'] + agg['SideBDeaths']

agg['WarID'] = agg['WarNum']
agg['PolityID'] = agg['CcodeA']
agg['PolityName'] = agg['CcodeA']

target = agg[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)