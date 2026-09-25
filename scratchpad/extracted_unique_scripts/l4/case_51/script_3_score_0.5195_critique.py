import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add PolityName column to df1 (missing in source1)
df1['PolityName'] = pd.NA

# Ensure consistent column order for joins
cols = ['Side', 'WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

# Convert columns to appropriate types
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

for df in [df0, df1, df2, df3]:
    df['Side'] = df['Side'].astype(str)
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    # PolityName is string in sources 0,2,3 but target expects integer, so convert if possible
    # But PolityName in target is integer, so convert PolityName to numeric (coerce errors)
    df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce').astype('Int64')

# Join df0 and df1 on Side, WarID, PolityID
df01 = pd.merge(df0, df1, on=['Side', 'WarID', 'PolityID'], how='outer', suffixes=('_0', '_1'))

# Join df01 with df2
df012 = pd.merge(df01, df2, on=['Side', 'WarID', 'PolityID'], how='outer', suffixes=('', '_2'))

# Join df012 with df3
df_all = pd.merge(df012, df3, on=['Side', 'WarID', 'PolityID'], how='outer', suffixes=('', '_3'))

# Now we have columns from multiple sources with suffixes, need to combine them into single columns

def coalesce_columns(df, base_col):
    # Collect all columns that start with base_col (including base_col itself)
    candidates = [c for c in df.columns if c == base_col or c.startswith(base_col + '_')]
    # Coalesce by taking first non-null value row-wise
    return df[candidates].bfill(axis=1).iloc[:, 0]

# For columns in target schema except keys, coalesce values from all sources
final_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

result = pd.DataFrame()
result['Side'] = df_all['Side']  # keys, no suffixes
result['WarID'] = df_all['WarID']
result['PolityID'] = df_all['PolityID']

for col in final_cols[3:]:  # skip keys
    result[col] = coalesce_columns(df_all, col)

# Now group by keys and aggregate
# Aggregations:
# For StartYear, StartMonth, StartDay, EndYear, EndMonth, EndDay, IsInitiator, Outcome, PolityName: take first non-null
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

result = result.groupby(['Side', 'WarID', 'PolityID'], dropna=False).agg(agg_dict).reset_index()

# Convert all columns to integer types as in target schema
for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']:
    result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)

result['Side'] = result['Side'].astype(str)

# Reorder columns exactly as target schema
result = result[['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)