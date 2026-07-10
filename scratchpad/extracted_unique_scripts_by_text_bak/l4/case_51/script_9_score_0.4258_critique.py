import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add PolityName column to df1 (missing in source1)
df1['PolityName'] = pd.NA

# Ensure all columns present and in same order for join
cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

# Convert PolityName to string for consistent processing
for df in [df0, df1, df2, df3]:
    df['PolityName'] = df['PolityName'].astype('string')

# Join df0 and df1 on ['WarID', 'PolityID', 'Side']
df01 = pd.merge(df0, df1, on=['WarID', 'PolityID', 'Side'], how='outer', suffixes=('_0', '_1'))

# Join result with df2
df012 = pd.merge(df01, df2, on=['WarID', 'PolityID', 'Side'], how='outer', suffixes=('', '_2'))

# Join result with df3
df_all = pd.merge(df012, df3, on=['WarID', 'PolityID', 'Side'], how='outer', suffixes=('', '_3'))

# Now, consolidate columns from all sources:
# For each attribute, pick the first non-null value from the multiple columns

def coalesce_columns(df, col_patterns):
    # col_patterns: list of column names to coalesce in order
    for col in col_patterns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[col_patterns].bfill(axis=1).iloc[:, 0]

# Columns to consolidate (excluding keys)
attributes = ['PolityName', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

# For each attribute, find all columns with that attribute name or with suffixes
consolidated = {}
for attr in attributes:
    cols_to_coalesce = [c for c in df_all.columns if c == attr or c.startswith(attr + '_')]
    consolidated[attr] = coalesce_columns(df_all, cols_to_coalesce)

# Build a DataFrame with keys and consolidated columns
df_final = pd.DataFrame({
    'Side': df_all['Side'],
    'WarID': df_all['WarID'],
    'PolityID': df_all['PolityID'],
    'PolityName': consolidated['PolityName'],
    'StartYear': consolidated['StartYear'],
    'StartMonth': consolidated['StartMonth'],
    'StartDay': consolidated['StartDay'],
    'EndYear': consolidated['EndYear'],
    'EndMonth': consolidated['EndMonth'],
    'EndDay': consolidated['EndDay'],
    'IsInitiator': consolidated['IsInitiator'],
    'Outcome': consolidated['Outcome'],
    'Deaths': consolidated['Deaths'],
})

# Convert columns to appropriate types
df_final['Side'] = df_final['Side'].astype(str)

int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# PolityName is string, convert to integer codes (factorize)
# Missing PolityName will be NaN, factorize assigns -1 to NaN, so replace -1 with pd.NA
codes, uniques = pd.factorize(df_final['PolityName'])
codes = pd.Series(codes)
codes = codes.replace(-1, pd.NA)
df_final['PolityName'] = codes.astype('Int64')

# Group by keys and aggregate
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'IsInitiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': 'first',
}

df_grouped = df_final.groupby(['Side', 'WarID', 'PolityID'], dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
final_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

df_grouped = df_grouped[final_cols]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)