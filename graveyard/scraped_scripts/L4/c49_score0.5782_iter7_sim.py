import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df0['SideA'] = df0['SideA'].fillna('')
df0['SideB'] = df0['SideB'].fillna('')

# Prepare two dataframes for the two sides of the war, to pivot longer
sideA_cols = ['WarNum', 'WarName', 'CcodeA', 'SideA', 'Intnl', 'Initiator', 'Outcome',
              'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1',
              'SideADeaths']
sideB_cols = ['WarNum', 'WarName', 'CcodeB', 'SideB', 'Intnl', 'Initiator', 'Outcome',
              'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2',
              'SideBDeaths']

df_sideA = df0[sideA_cols].copy()
df_sideA = df_sideA.rename(columns={
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

df_sideB = df0[sideB_cols].copy()
df_sideB = df_sideB.rename(columns={
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
})

# Concatenate the two sides vertically
df_long = pd.concat([df_sideA, df_sideB], ignore_index=True)

# Remove rows where PolityName is empty or NaN (no polity info)
df_long = df_long[df_long['PolityName'].notna() & (df_long['PolityName'] != '')]

# Convert columns to correct types
int_cols = ['WarNum', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']
for col in int_cols:
    df_long[col] = pd.to_numeric(df_long[col], errors='coerce').fillna(0).astype(int)

df_long = df_long.rename(columns={'WarNum': 'WarID'})

# Reorder columns to target schema
df_long = df_long[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
                   'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_long.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)