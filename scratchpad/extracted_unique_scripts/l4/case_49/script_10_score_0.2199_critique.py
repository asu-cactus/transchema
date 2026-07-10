import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

sideA = pd.DataFrame({
    'PolityName': df0['SideA'],
    'WarID': pd.to_numeric(df0['WarNum'], errors='coerce').astype('Int64'),
    'PolityID': pd.to_numeric(df0['CcodeA'], errors='coerce').astype('Int64'),
    'StartMonth': pd.to_numeric(df0['StartMonth1'], errors='coerce').astype('Int64'),
    'StartDay': pd.to_numeric(df0['StartDay1'], errors='coerce').astype('Int64'),
    'StartYear': pd.to_numeric(df0['StartYear1'], errors='coerce').astype('Int64'),
    'EndMonth': pd.to_numeric(df0['EndMonth1'], errors='coerce').astype('Int64'),
    'EndDay': pd.to_numeric(df0['EndDay1'], errors='coerce').astype('Int64'),
    'EndYear': pd.to_numeric(df0['EndYear1'], errors='coerce').astype('Int64'),
    'Initiator': pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64'),
    'Outcome': pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64'),
    'Deaths': pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype('Int64')
})

sideB = pd.DataFrame({
    'PolityName': df0['SideB'],
    'WarID': pd.to_numeric(df0['WarNum'], errors='coerce').astype('Int64'),
    'PolityID': pd.to_numeric(df0['CcodeB'], errors='coerce').astype('Int64'),
    'StartMonth': pd.to_numeric(df0['StartMonth1'], errors='coerce').astype('Int64'),
    'StartDay': pd.to_numeric(df0['StartDay1'], errors='coerce').astype('Int64'),
    'StartYear': pd.to_numeric(df0['StartYear1'], errors='coerce').astype('Int64'),
    'EndMonth': pd.to_numeric(df0['EndMonth1'], errors='coerce').astype('Int64'),
    'EndDay': pd.to_numeric(df0['EndDay1'], errors='coerce').astype('Int64'),
    'EndYear': pd.to_numeric(df0['EndYear1'], errors='coerce').astype('Int64'),
    'Initiator': pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64'),
    'Outcome': pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64'),
    'Deaths': pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype('Int64')
})

df = pd.concat([sideA, sideB], ignore_index=True)

df = df[df['PolityName'].notna()]
df = df[df['PolityName'] != '']

group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

result = df.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

result['Deaths'] = result['Deaths'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)