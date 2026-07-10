import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Prepare SideA dataframe
df_sideA = pd.DataFrame()
df_sideA['PolityName'] = df['SideA'].fillna('')
df_sideA['WarID'] = df['WarNum'].astype('Int64')
df_sideA['PolityID'] = 0
df_sideA['StartMonth'] = df['StartMonth1'].fillna(1).astype('Int64')
df_sideA['StartDay'] = df['StartDay1'].fillna(1).astype('Int64')
df_sideA['StartYear'] = df['StartYear1'].fillna(1).astype('Int64')
df_sideA['EndMonth'] = df['EndMonth1'].fillna(1).astype('Int64')
df_sideA['EndDay'] = df['EndDay1'].fillna(1).astype('Int64')
df_sideA['EndYear'] = df['EndYear1'].fillna(1).astype('Int64')
df_sideA['Initiator'] = df['Initiator']
df_sideA['Outcome'] = df['Outcome'].astype('Int64')
df_sideA['Deaths'] = df['SideADeaths'].fillna(0).astype('Int64')

# Prepare SideB dataframe
df_sideB = pd.DataFrame()
df_sideB['PolityName'] = df['SideB'].fillna('')
df_sideB['WarID'] = df['WarNum'].astype('Int64')
df_sideB['PolityID'] = 0
df_sideB['StartMonth'] = df['StartMonth1'].fillna(1).astype('Int64')
df_sideB['StartDay'] = df['StartDay1'].fillna(1).astype('Int64')
df_sideB['StartYear'] = df['StartYear1'].fillna(1).astype('Int64')
df_sideB['EndMonth'] = df['EndMonth1'].fillna(1).astype('Int64')
df_sideB['EndDay'] = df['EndDay1'].fillna(1).astype('Int64')
df_sideB['EndYear'] = df['EndYear1'].fillna(1).astype('Int64')
df_sideB['Initiator'] = df['Initiator']
df_sideB['Outcome'] = df['Outcome'].astype('Int64')
df_sideB['Deaths'] = df['SideBDeaths'].fillna(0).astype('Int64')

# Concatenate SideA and SideB dataframes
df_out = pd.concat([df_sideA, df_sideB], ignore_index=True)

# Remove rows where PolityName is empty string (no polity)
df_out = df_out[df_out['PolityName'] != '']

# Map Initiator string to integer IDs
df_out['Initiator'], _ = pd.factorize(df_out['Initiator'])

# Group by all key columns except Deaths, sum Deaths
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

df_final = df_out.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure correct dtypes
df_final['PolityName'] = df_final['PolityName'].astype(str)
df_final['WarID'] = df_final['WarID'].astype('Int64')
df_final['PolityID'] = df_final['PolityID'].astype('Int64')
df_final['StartMonth'] = df_final['StartMonth'].astype('Int64')
df_final['StartDay'] = df_final['StartDay'].astype('Int64')
df_final['StartYear'] = df_final['StartYear'].astype('Int64')
df_final['EndMonth'] = df_final['EndMonth'].astype('Int64')
df_final['EndDay'] = df_final['EndDay'].astype('Int64')
df_final['EndYear'] = df_final['EndYear'].astype('Int64')
df_final['Initiator'] = df_final['Initiator'].astype('Int64')
df_final['Outcome'] = df_final['Outcome'].astype('Int64')
df_final['Deaths'] = df_final['Deaths'].astype('Int64')

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)