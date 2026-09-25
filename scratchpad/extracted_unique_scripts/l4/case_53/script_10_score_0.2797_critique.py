import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Add PolityName column to df2 if missing
if 'PolityName' not in df2.columns:
    df2['PolityName'] = pd.NA

# Ensure PolityName is string type for all
for df in [df0, df1, df2, df3]:
    df['PolityName'] = df['PolityName'].astype('string')

# Concatenate all dataframes (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

# Convert columns to appropriate types
df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')

# Map Side from 'A'/'B' to 1/2, keep NaN as is
side_map = {'A': 1, 'B': 2}
df_all['Side'] = df_all['Side'].map(side_map).astype('Int64')

df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').astype('Int64')
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').astype('Int64')

# Select and reorder columns as per target schema
df_all = df_all[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

# Group by the composite key columns and aggregate
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'min',
    'EndMonth': 'min',
    'EndDay': 'min',
    'Side': 'min',
    'IsInitiator': 'min',
    'Outcome': 'min',
    'Deaths': 'sum'
}

df_grouped = df_all.groupby(['PolityName', 'WarID', 'PolityID'], dropna=False, as_index=False).agg(agg_dict)

# Write to output CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)