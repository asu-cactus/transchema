import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    # Source4_52_3 missing PolityName column, add it with NaN
    if i == 3 and 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    dfs.append(df)

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Columns in target schema
cols_target = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Keep only target columns (some source tables may have extra columns)
df_all = df_all[cols_target]

# Convert columns to appropriate types
# For grouping columns: convert to Int64 (nullable integer)
group_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome']

for col in group_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Deaths: convert to numeric, fill NaN with 0 for aggregation
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').fillna(0).astype('Int64')

# PolityName: factorize strings to integers, keep NaN as is
# First fill NaN with a placeholder string to factorize properly
df_all['PolityName'] = df_all['PolityName'].fillna('')

# Factorize PolityName
codes, uniques = pd.factorize(df_all['PolityName'])
df_all['PolityName'] = codes.astype('Int64')  # -1 for NaN replaced by -1

# Replace -1 with pd.NA to keep consistency
df_all.loc[df_all['PolityName'] == -1, 'PolityName'] = pd.NA

# Group by key columns, aggregate Deaths by sum, PolityName by first (non-null)
agg_dict = {
    'Deaths': 'sum',
    'PolityName': 'first'
}

df_grouped = df_all.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Convert all columns to int (nullable Int64), fill NaN in PolityName with 0 (as target examples have integers)
df_grouped['PolityName'] = df_grouped['PolityName'].fillna(0).astype('Int64')

# Ensure all columns are Int64
for col in cols_target:
    if col not in df_grouped.columns:
        continue
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').astype('Int64')

# Reorder columns to target schema
df_grouped = df_grouped[cols_target]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)