import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Align columns: Source1 lacks PolityName, add it with NaN
df1['PolityName'] = pd.NA

# Ensure all columns are in the same order and all present
cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Reorder and select columns for each df
df0 = df0[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]
df1 = df1[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]
df2 = df2[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]
df3 = df3[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert columns to target types
df['Side'] = df['Side'].astype(str)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['IsInitiator'] = pd.to_numeric(df['IsInitiator'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')
df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)