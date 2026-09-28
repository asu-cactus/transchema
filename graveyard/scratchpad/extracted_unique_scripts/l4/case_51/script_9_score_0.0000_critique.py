import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add PolityName column to df1 (missing in source1)
df1['PolityName'] = pd.NA

# Convert PolityName to string to unify types before join (some are string, some NA)
for df in [df0, df1, df2, df3]:
    df['PolityName'] = df['PolityName'].astype('string')

# Define join keys
join_keys = ['WarID', 'PolityID', 'Side']

# Join df0 and df1
df01 = pd.merge(df0, df1, on=join_keys, how='inner', suffixes=('_0', '_1'))

# Join df01 and df2
df012 = pd.merge(df01, df2, on=join_keys, how='inner', suffixes=('', '_2'))

# Join df012 and df3
df_all = pd.merge(df012, df3, on=join_keys, how='inner', suffixes=('', '_3'))

# Helper function to coalesce columns from multiple sources, preferring non-null values in order
def coalesce_columns(df, col_base, suffixes):
    cols = [col_base + s for s in suffixes if col_base + s in df.columns]
    # Return first non-null value across these columns row-wise
    return df[cols].bfill(axis=1).iloc[:, 0]

# Columns to coalesce (all except join keys)
cols_to_coalesce = ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay',
                    'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Suffixes from sources in order of preference (0,1,2,3)
suffixes = ['', '_0', '_1', '_2', '_3']

# For each column, coalesce values from all sources
for col in cols_to_coalesce:
    # Collect all variants of the column in df_all
    variants = [col + s for s in suffixes if col + s in df_all.columns]
    if variants:
        df_all[col] = df_all[variants].bfill(axis=1).iloc[:, 0]
    else:
        # If column missing, fill with NA
        df_all[col] = pd.NA

# Keep only needed columns: join keys + coalesced columns
final_cols = join_keys + cols_to_coalesce
df_final = df_all[final_cols]

# Convert types according to target schema
# Target schema: ['Side': string, 'WarID': int, 'PolityID': int, 'StartYear': int, 'StartMonth': int, 'StartDay': int,
# 'EndYear': int, 'EndMonth': int, 'EndDay': int, 'IsInitiator': int, 'Outcome': int, 'Deaths': int, 'PolityName': int]

df_final['Side'] = df_final['Side'].astype(str)

int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# Group by Side, WarID, PolityID
# Aggregations:
# For date and categorical columns: take first (assuming consistent per group)
# For Deaths: sum

agg_dict = {
    'StartYear': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'IsInitiator': 'first',
    'Outcome': 'first',
    'Deaths': 'sum',
    'PolityName': 'first'
}

df_grouped = df_final.groupby(['Side', 'WarID', 'PolityID'], dropna=False, as_index=False).agg(agg_dict)

# Ensure column order as target schema
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

df_grouped = df_grouped[target_cols]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)