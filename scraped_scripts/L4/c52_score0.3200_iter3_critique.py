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

df_all = pd.concat(dfs, ignore_index=True)

# Ensure PolityName column exists (Source4_52_3 lacks it)
if 'PolityName' not in df_all.columns:
    df_all['PolityName'] = pd.NA

# Encode PolityName as categorical codes (target expects integer)
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA)

# Encode Side as categorical codes (target expects integer)
df_all['Side'] = df_all['Side'].astype('category').cat.codes.replace(-1, pd.NA)

# Convert all relevant columns to numeric with nullable integer dtype
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    if col in df_all.columns:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Define group by columns
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay']

# Aggregate columns and functions
agg_dict = {
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': 'max'
}

df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_out = df_grouped[target_cols]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)