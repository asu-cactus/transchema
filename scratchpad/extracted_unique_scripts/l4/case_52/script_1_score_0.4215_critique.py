import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    # Ensure PolityName exists in all sources (Source3 missing PolityName)
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    dfs.append(df)

# UNION all sources
df_all = pd.concat(dfs, ignore_index=True)

# Convert PolityName to categorical codes (integer), keep NaN as pd.NA
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA)

# Convert Side from string to categorical codes (integer), keep NaN as pd.NA
df_all['Side'] = df_all['Side'].astype('category').cat.codes.replace(-1, pd.NA)

# Ensure all target columns exist
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in target_cols:
    if col not in df_all.columns:
        df_all[col] = pd.NA

# Cast columns to numeric with nullable integer dtype where possible
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Group by leftmost columns: IsInitiator, WarID, PolityID
# Aggregate other columns appropriately:
# StartYear, StartMonth, StartDay: min (earliest start)
# EndYear, EndMonth, EndDay: max (latest end)
# Side, Outcome, PolityName: max (categorical codes)
# Deaths: sum

agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': 'max',
}

df_grouped = df_all.groupby(['IsInitiator', 'WarID', 'PolityID'], dropna=False, observed=False).agg(agg_dict).reset_index()

# Reorder columns to target schema
df_grouped = df_grouped[target_cols]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)