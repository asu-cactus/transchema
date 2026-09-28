import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

dfs = [df0, df1, df2, df3]

for i, df in enumerate(dfs):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    if 'PolityID' not in df.columns:
        df['PolityID'] = pd.NA
    # Ensure all columns exist in all dfs
    expected_cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
    missing_cols = set(expected_cols) - set(df.columns)
    for c in missing_cols:
        df[c] = pd.NA
    dfs[i] = df[expected_cols]

df_all = pd.concat(dfs, ignore_index=True)

df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').fillna(0).astype(int)
df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')

# Convert Side, Outcome, Deaths, PolityName to integer as target schema requires
# Side and Outcome columns in source are sometimes strings (e.g. 'A', 'B'), convert them to integer codes
df_all['Side'] = df_all['Side'].astype('string').str.strip()
side_mapping = {v: i for i, v in enumerate(sorted(df_all['Side'].dropna().unique()))}
df_all['Side'] = df_all['Side'].map(side_mapping).astype('Int64')

df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').astype('Int64')

# PolityName in target schema is integer, convert string PolityName to integer codes
df_all['PolityName'] = df_all['PolityName'].astype('string').str.strip()
polityname_mapping = {v: i for i, v in enumerate(sorted(df_all['PolityName'].dropna().unique()))}
df_all['PolityName'] = df_all['PolityName'].map(polityname_mapping).astype('Int64')

df_all = df_all[['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)