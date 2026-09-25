import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df['SideADeaths'] = pd.to_numeric(df['SideADeaths'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
df['SideBDeaths'] = pd.to_numeric(df['SideBDeaths'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
df['WarNum'] = pd.to_numeric(df['WarNum'], errors='coerce').fillna(0).astype(int)
df['CcodeA'] = pd.to_numeric(df['CcodeA'], errors='coerce').fillna(0).astype(int)

grouped = df.groupby(['WarNum', 'CcodeA', 'WarName'], as_index=False).agg(
    SideADeaths_sum=('SideADeaths', 'sum'),
    SideBDeaths_sum=('SideBDeaths', 'sum'),
    WarNum_count=('WarNum', 'count')
)

grouped['Deaths'] = grouped['SideADeaths_sum'] + grouped['SideBDeaths_sum']

grouped.rename(columns={
    'WarName': 'PolityName',
    'WarNum': 'WarID',
    'CcodeA': 'PolityID'
}, inplace=True)

grouped['StartMonth'] = 1
grouped['StartDay'] = 1
grouped['StartYear'] = 1
grouped['EndMonth'] = 1
grouped['EndDay'] = 1
grouped['EndYear'] = 1
grouped['Initiator'] = 2
grouped['Outcome'] = 2

final_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

result = grouped[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)