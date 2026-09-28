import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add PolityName column to df1 (missing in Source1)
df1['PolityName'] = pd.NA

# Define join keys (common columns to join on)
join_keys = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
             'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']

# Convert join keys to consistent types before join to avoid mismatches
for df in [df0, df1, df2, df3]:
    df['Side'] = df['Side'].astype(str)
    for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Join df0 and df1
df01 = pd.merge(df0, df1, on=join_keys + ['Side', 'WarID', 'PolityID'], how='inner', suffixes=('_0', '_1'))

# Because we joined on all keys including Side, WarID, PolityID, the suffixes are redundant for keys
# But Deaths and PolityName columns are duplicated, keep Deaths_0 and Deaths_1, PolityName_0 and PolityName_1

# Join df01 with df2
df2['Side'] = df2['Side'].astype(str)
for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']:
    df2[col] = pd.to_numeric(df2[col], errors='coerce').astype('Int64')

df012 = pd.merge(df01, df2, on=join_keys + ['Side', 'WarID', 'PolityID'], how='inner', suffixes=('', '_2'))

# Join df012 with df3
df3['Side'] = df3['Side'].astype(str)
for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']:
    df3[col] = pd.to_numeric(df3[col], errors='coerce').astype('Int64')

df_all = pd.merge(df012, df3, on=join_keys + ['Side', 'WarID', 'PolityID'], how='inner', suffixes=('', '_3'))

# Now aggregate:
# Group by leftmost columns of target schema (excluding Deaths and PolityName)
group_by_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']

# Sum Deaths columns from all sources (Deaths_0, Deaths_1, Deaths, Deaths_2, Deaths_3)
# Deaths columns may have suffixes or not depending on merge
# Collect all Deaths columns
death_cols = [col for col in df_all.columns if col.startswith('Deaths')]
# Sum deaths row-wise
df_all['Deaths_sum'] = df_all[death_cols].sum(axis=1, skipna=True)

# For PolityName, take first non-null from any PolityName columns
# PolityName columns may be: PolityName_0, PolityName_1, PolityName, PolityName_2, PolityName_3
polityname_cols = [col for col in df_all.columns if col.startswith('PolityName')]

def first_non_null(row):
    for col in polityname_cols:
        val = row[col]
        if pd.notna(val):
            return val
    return pd.NA

df_all['PolityName_str'] = df_all.apply(first_non_null, axis=1)

# Map PolityName strings to integer IDs (factorize)
df_all['PolityName'] = pd.factorize(df_all['PolityName_str'])[0]
# factorize returns -1 for NaN, convert -1 to pd.NA
df_all.loc[df_all['PolityName'] == -1, 'PolityName'] = pd.NA
df_all['PolityName'] = df_all['PolityName'].astype('Int64')

# Prepare final dataframe with target schema columns
final_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

df_final = df_all[group_by_cols + ['Deaths_sum', 'PolityName']].copy()
df_final.rename(columns={'Deaths_sum': 'Deaths'}, inplace=True)

# Group by keys and aggregate Deaths by sum, PolityName by first (already done by factorize, so take max)
# Since after join, duplicates may exist, group again to ensure uniqueness

agg_dict = {
    'Deaths': 'sum',
    'PolityName': 'max'  # max to get the integer ID (first non-null)
}

df_final = df_final.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Convert types to target schema
df_final['Side'] = df_final['Side'].astype(str)
for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)