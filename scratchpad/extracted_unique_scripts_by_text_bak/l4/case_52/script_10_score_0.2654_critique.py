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
    # Add missing PolityName column if not present (Source4_52_3)
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure all expected columns exist
expected_cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
for col in expected_cols:
    if col not in df_all.columns:
        df_all[col] = pd.NA

df_all = df_all[expected_cols]

# Convert columns to appropriate types
# PolityName is string in source but integer in target, factorize it
df_all['PolityName'] = pd.factorize(df_all['PolityName'].astype(str))[0]

# Convert other columns to Int64 (nullable integer)
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths']

for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Define group by columns (leftmost columns of target schema except Deaths and PolityName)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome']

# Aggregate Deaths by sum, PolityName by first
agg_dict = {
    'Deaths': 'sum',
    'PolityName': 'first'
}

df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to target schema order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_grouped = df_grouped[target_cols]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)