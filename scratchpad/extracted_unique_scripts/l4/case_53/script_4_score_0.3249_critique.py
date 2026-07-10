import pandas as pd

# Read sources with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Ensure PolityName column exists in all dataframes
def ensure_polityname(df):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    return df

df0 = ensure_polityname(df0)
df1 = ensure_polityname(df1)
df2 = ensure_polityname(df2)
df3 = ensure_polityname(df3)

# Define common columns in target schema order
common_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Select and reorder columns to common_cols, fill missing columns with NA if any
def select_and_order(df):
    # Add missing columns with NA if any
    for col in common_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df[common_cols]

df0 = select_and_order(df0)
df1 = select_and_order(df1)
df2 = select_and_order(df2)
df3 = select_and_order(df3)

# Concatenate all dataframes (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert PolityName to string type
df_all['PolityName'] = df_all['PolityName'].astype('string')

# Convert integer columns to numeric, coercing errors to NaN, then fill NaN with 0 and convert to int
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Group by the leftmost unique columns: PolityName, WarID, PolityID
# Aggregate other columns:
# For date and categorical columns, take min (assuming consistent per group)
# For Deaths, sum
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

# Reorder columns to target schema order (should already be correct)
df_grouped = df_grouped[common_cols]

# Write to CSV without index
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)