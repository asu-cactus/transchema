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

# Add missing columns to each df to match union schema
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for i, df in enumerate(dfs):
    for col in target_cols:
        if col not in df.columns:
            df[col] = pd.NA
    dfs[i] = df[target_cols]

df_all = pd.concat(dfs, ignore_index=True, sort=False)

# Map Side from string to integer if needed
if df_all['Side'].dtype == object:
    side_map = {v: i for i, v in enumerate(sorted(df_all['Side'].dropna().unique()))}
    df_all['Side'] = df_all['Side'].map(side_map).astype('Int64')

# Map PolityName from string to integer if needed
if df_all['PolityName'].dtype == object:
    polity_map = {v: i for i, v in enumerate(sorted(df_all['PolityName'].dropna().unique()))}
    df_all['PolityName'] = df_all['PolityName'].map(polity_map).astype('Int64')

# Convert other columns to integer or nullable integer as appropriate
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Outcome']
for col in int_cols:
    if col in df_all.columns:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Deaths: convert to numeric float, then to Int64 if all integer-like
if 'Deaths' in df_all.columns:
    df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce')
    if df_all['Deaths'].dropna().apply(float.is_integer).all():
        df_all['Deaths'] = df_all['Deaths'].astype('Int64')

# Group by all identifying columns except Deaths, aggregate Deaths by sum
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure final columns order matches target schema
df_grouped = df_grouped[target_cols]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)