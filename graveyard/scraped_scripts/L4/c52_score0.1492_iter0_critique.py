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
df_all = pd.concat(dfs, ignore_index=True)

# Target columns and order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Convert PolityName to numeric (integer) with coercion
df_all['PolityName'] = pd.to_numeric(df_all.get('PolityName', pd.Series(dtype='object')), errors='coerce')

# Convert Side from string to integer by factorizing (if needed)
if 'Side' in df_all.columns and df_all['Side'].dtype == object:
    df_all['Side'] = pd.factorize(df_all['Side'])[0] + 1

# Convert all relevant columns to numeric with coercion, then to nullable Int64 where appropriate
for col in target_cols:
    if col in df_all.columns:
        if col == 'PolityName':
            df_all[col] = df_all[col].astype('Int64')
        elif col == 'Side':
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')
        elif col in ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                     'EndYear', 'EndMonth', 'EndDay', 'Outcome']:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')
        elif col == 'Deaths':
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')
    else:
        df_all[col] = pd.NA

# Group by key columns and aggregate others
group_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear']

agg_dict = {
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Side': 'first',
    'Outcome': 'first',
    'Deaths': 'sum',
    'PolityName': 'first'
}

df_grouped = df_all.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to target schema
df_grouped = df_grouped[target_cols]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)