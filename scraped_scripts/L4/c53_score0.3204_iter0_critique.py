import pandas as pd
import numpy as np

# Read all source files with index_col=0 to ignore the first numerical index column
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

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

# Convert PolityName to string type
df_all['PolityName'] = df_all['PolityName'].astype('string')

# Select and reorder columns as per target schema
cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
df_all = df_all[cols]

# Convert columns to appropriate types with coercion
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']
for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Convert Side column: map letters to integers (A=1, B=2, etc.) or keep numeric
def side_to_int(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, (int, np.integer)):
        return x
    if isinstance(x, float):
        if np.isnan(x):
            return pd.NA
        return int(x)
    if isinstance(x, str):
        x = x.strip()
        if x.isdigit():
            return int(x)
        if len(x) == 1 and x.isalpha():
            return ord(x.upper()) - ord('A') + 1
    return pd.NA

df_all['Side'] = df_all['Side'].apply(side_to_int).astype('Int64')

# Group by the composite key and aggregate
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

# Ensure columns order and types match target schema exactly
df_grouped = df_grouped[cols]

# Convert all integer columns to Int64 nullable type again (aggregation may change types)
for col in cols:
    if col != 'PolityName':
        df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').astype('Int64')

# Write to output CSV without index
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)