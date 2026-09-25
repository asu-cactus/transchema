import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert PolityName to numeric (target expects integer)
df_all['PolityName'] = pd.to_numeric(df_all.get('PolityName', pd.Series(dtype='float')), errors='coerce')

# Ensure all target columns exist
cols_target = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for c in cols_target:
    if c not in df_all.columns:
        df_all[c] = pd.NA

# Convert all columns to numeric with nullable integer dtype where possible
for c in cols_target:
    df_all[c] = pd.to_numeric(df_all[c], errors='coerce').astype('Int64')

# Define group by columns
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear']

# Aggregations:
# Sum Deaths
# For other columns, take first non-null value
agg_dict = {
    'Deaths': 'sum',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Side': 'first',
    'Outcome': 'first',
    'PolityName': 'first'
}

df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to target schema
df_grouped = df_grouped[cols_target]

# Convert all columns to Int64 again to ensure type consistency
for c in cols_target:
    df_grouped[c] = pd.to_numeric(df_grouped[c], errors='coerce').astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)