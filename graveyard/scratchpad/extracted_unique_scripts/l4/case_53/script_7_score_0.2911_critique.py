import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Convert PolityID to Int64 to handle NaNs properly
for df in [df0, df1, df2, df3]:
    df['PolityID'] = df['PolityID'].astype('Int64')

# Standardize Side column: map 'A'->1, 'B'->2, keep numeric as is
def standardize_side(df):
    if df['Side'].dtype == object:
        df['Side'] = df['Side'].replace({'A':1, 'B':2})
    df['Side'] = df['Side'].astype('Int64')
    return df

for df in [df0, df1, df2, df3]:
    df = standardize_side(df)

# Convert other integer columns to Int64 to handle NaNs
int_cols = ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay',
            'IsInitiator', 'Outcome', 'Deaths']

for df in [df0, df1, df2, df3]:
    for col in int_cols:
        # Deaths can be float in source, convert to Int64 after filling NaNs with 0
        if col == 'Deaths':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# PolityName is missing in df2, fill it by joining with df0 on WarID and PolityID
# Use left join to keep all rows in df2
df0_name = df0[['WarID', 'PolityID', 'PolityName']].drop_duplicates()
df2 = df2.merge(df0_name, on=['WarID', 'PolityID'], how='left')

# For rows in df2 still missing PolityName, try to fill from df1 and df3 as well
# Merge with df1
df1_name = df1[['WarID', 'PolityID', 'PolityName']].drop_duplicates()
df2 = df2.merge(df1_name, on=['WarID', 'PolityID'], how='left', suffixes=('', '_1'))

# Coalesce PolityName columns
df2['PolityName'] = df2['PolityName'].combine_first(df2['PolityName_1'])
df2 = df2.drop(columns=['PolityName_1'])

# For any remaining missing PolityName in df2, try df3
df3_name = df3[['WarID', 'PolityID', 'PolityName']].drop_duplicates()
df2 = df2.merge(df3_name, on=['WarID', 'PolityID'], how='left', suffixes=('', '_3'))
df2['PolityName'] = df2['PolityName'].combine_first(df2['PolityName_3'])
df2 = df2.drop(columns=['PolityName_3'])

# Convert PolityName to string type
for df in [df0, df1, df2, df3]:
    df['PolityName'] = df['PolityName'].astype('string')

# Now union all four dataframes
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

# Ensure all columns exist in df_all, fill missing with NaN or 0 for Deaths
expected_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in expected_cols:
    if col not in df_all.columns:
        if col == 'Deaths':
            df_all[col] = 0
        else:
            df_all[col] = pd.NA

# Reorder columns
df_all = df_all[expected_cols]

# Convert columns to correct types again after concat
df_all['PolityName'] = df_all['PolityName'].astype('string')
df_all['WarID'] = df_all['WarID'].astype('Int64')
df_all['PolityID'] = df_all['PolityID'].astype('Int64')
for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay',
            'Side', 'IsInitiator', 'Outcome', 'Deaths']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype('Int64')

# Group by all leftmost columns except Deaths, aggregate Deaths by sum
group_by_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

df_final = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths':'sum'})

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)