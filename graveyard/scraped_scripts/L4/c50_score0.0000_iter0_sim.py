import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df0['PolityID'] = df0['CcodeA'].fillna(df0['CcodeB'])
df0['PolityName'] = df0['SideA'].fillna(df0['SideB'])

df0['StartMonth'] = df0['StartMonth1'].fillna(df0['StartMonth2'])
df0['StartDay'] = df0['StartDay1'].fillna(df0['StartDay2'])
df0['StartYear'] = df0['StartYear1'].fillna(df0['StartYear2'])

df0['EndMonth'] = df0['EndMonth1'].fillna(df0['EndMonth2'])
df0['EndDay'] = df0['EndDay1'].fillna(df0['EndDay2'])
df0['EndYear'] = df0['EndYear1'].fillna(df0['EndYear2'])

df0['Deaths'] = df0['SideADeaths'].fillna(0) + df0['SideBDeaths'].fillna(0)

grouped = df0.groupby('Outcome', as_index=False).agg({
    'WarNum': 'first',
    'PolityID': 'first',
    'PolityName': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'StartYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'EndYear': 'first',
    'Initiator': 'first',
    'Deaths': 'sum'
})

grouped = grouped.rename(columns={
    'WarNum': 'WarID'
})

cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
        'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']

result = grouped[cols]

for c in ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
          'EndMonth', 'EndDay', 'EndYear', 'Deaths']:
    result[c] = pd.to_numeric(result[c], errors='coerce').fillna(0).astype(int)

result['PolityName'] = result['PolityName'].apply(lambda x: int(x) if pd.notna(x) and str(x).isdigit() else 0)

result['Initiator'] = result['Initiator'].apply(lambda x: int(x) if pd.notna(x) and str(x).isdigit() else 0)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)