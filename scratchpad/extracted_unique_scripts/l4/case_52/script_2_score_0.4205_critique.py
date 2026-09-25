import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True, sort=False)

# Convert columns to target types
df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').fillna(0).astype(int)
df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')

# Side column: convert string labels to integer codes
df_all['Side'] = df_all['Side'].astype(str)
side_mapping = {v: i for i, v in enumerate(sorted(df_all['Side'].dropna().unique()))}
df_all['Side'] = df_all['Side'].map(side_mapping).astype('Int64')

# Outcome and Deaths to integer (Deaths may be float, convert by rounding)
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').fillna(0).astype(int)
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').round().fillna(0).astype(int)

# PolityName: convert string to integer by factorize (handle missing PolityName in Source4_52_3)
df_all['PolityName'] = df_all['PolityName'].fillna('')  # fill NaN with empty string for factorize
df_all['PolityName'] = pd.factorize(df_all['PolityName'].astype(str))[0].astype(int)

# Group by all columns except Deaths, aggregate Deaths by sum
group_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

df_grouped = df_all.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Reorder columns as per target schema
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_target = df_grouped[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)