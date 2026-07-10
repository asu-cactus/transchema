import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="WarNum", suffixes=('_left', '_right'))

df_grouped = df_joined.groupby('Outcome').agg({
    'WarNum': 'first',
    'CcodeA_left': 'first',
    'SideA_left': 'first',
    'StartMonth1_left': 'first',
    'StartDay1_left': 'first',
    'StartYear1_left': 'first',
    'EndMonth1_left': 'first',
    'EndDay1_left': 'first',
    'EndYear1_left': 'first',
    'Initiator_left': 'first',
    'SideADeaths_left': 'sum',
    'SideBDeaths_left': 'sum'
}).reset_index()

df_grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA_left': 'PolityID',
    'SideA_left': 'PolityName',
    'StartMonth1_left': 'StartMonth',
    'StartDay1_left': 'StartDay',
    'StartYear1_left': 'StartYear',
    'EndMonth1_left': 'EndMonth',
    'EndDay1_left': 'EndDay',
    'EndYear1_left': 'EndYear',
    'Initiator_left': 'Initiator',
    'SideADeaths_left': 'Deaths'
}, inplace=True)

df_grouped['PolityName'] = pd.to_numeric(df_grouped['PolityName'], errors='coerce').fillna(0).astype(int)
df_grouped['Initiator'] = pd.to_numeric(df_grouped['Initiator'], errors='coerce').fillna(0).astype(int)
df_grouped['Outcome'] = pd.to_numeric(df_grouped['Outcome'], errors='coerce').fillna(0).astype(int)
df_grouped['WarID'] = pd.to_numeric(df_grouped['WarID'], errors='coerce').fillna(0).astype(int)
df_grouped['PolityID'] = pd.to_numeric(df_grouped['PolityID'], errors='coerce').fillna(0).astype(int)
df_grouped['StartMonth'] = pd.to_numeric(df_grouped['StartMonth'], errors='coerce').fillna(0).astype(int)
df_grouped['StartDay'] = pd.to_numeric(df_grouped['StartDay'], errors='coerce').fillna(0).astype(int)
df_grouped['StartYear'] = pd.to_numeric(df_grouped['StartYear'], errors='coerce').fillna(0).astype(int)
df_grouped['EndMonth'] = pd.to_numeric(df_grouped['EndMonth'], errors='coerce').fillna(0).astype(int)
df_grouped['EndDay'] = pd.to_numeric(df_grouped['EndDay'], errors='coerce').fillna(0).astype(int)
df_grouped['EndYear'] = pd.to_numeric(df_grouped['EndYear'], errors='coerce').fillna(0).astype(int)
df_grouped['Deaths'] = pd.to_numeric(df_grouped['Deaths'], errors='coerce').fillna(0).astype(int)

df_grouped = df_grouped[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)