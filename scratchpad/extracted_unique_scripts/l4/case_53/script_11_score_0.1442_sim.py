import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

df0_grouped = df0.groupby(['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], dropna=False, as_index=False)['Deaths'].sum()
df1_grouped = df1.groupby(['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], dropna=False, as_index=False)['Deaths'].sum()
df2_grouped = df2.groupby(['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], dropna=False, as_index=False)['Deaths'].sum()
df3_grouped = df3.groupby(['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], dropna=False, as_index=False)['Deaths'].sum()

# For df2_grouped, PolityName is missing, add it as NaN to align columns
df2_grouped['PolityName'] = pd.NA
df2_grouped = df2_grouped[['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

df0_grouped = df0_grouped[['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]
df1_grouped = df1_grouped[['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]
df3_grouped = df3_grouped[['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

union_df = pd.concat([df0_grouped, df1_grouped, df2_grouped, df3_grouped], ignore_index=True)

final_df = union_df.groupby(['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], dropna=False, as_index=False)['Deaths'].sum()

# Convert columns to target types
final_df['PolityName'] = final_df['PolityName'].astype('string')
final_df['WarID'] = final_df['WarID'].astype('Int64')
final_df['PolityID'] = final_df['PolityID'].astype('Int64')
final_df['StartYear'] = final_df['StartYear'].astype('Int64')
final_df['StartMonth'] = final_df['StartMonth'].astype('Int64')
final_df['StartDay'] = final_df['StartDay'].astype('Int64')
final_df['EndYear'] = final_df['EndYear'].astype('Int64')
final_df['EndMonth'] = final_df['EndMonth'].astype('Int64')
final_df['EndDay'] = final_df['EndDay'].astype('Int64')

# Side, IsInitiator, Outcome are integers but may be strings or objects, convert safely
final_df['Side'] = pd.to_numeric(final_df['Side'], errors='coerce').astype('Int64')
final_df['IsInitiator'] = pd.to_numeric(final_df['IsInitiator'], errors='coerce').astype('Int64')
final_df['Outcome'] = pd.to_numeric(final_df['Outcome'], errors='coerce').astype('Int64')

final_df['Deaths'] = final_df['Deaths'].fillna(0).astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)