import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Ensure all have PolityName column
for df in [df0, df1, df3]:
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
if 'PolityName' not in df2.columns:
    df2['PolityName'] = pd.NA

# Convert columns to consistent types
def convert_types(df):
    df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
    df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
    df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').fillna(0).astype(int)
    df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').fillna(0).astype(int)
    df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
    df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').fillna(0).astype(int)
    df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').fillna(0).astype(int)
    # Side conversion
    def side_to_int(x):
        if pd.isna(x):
            return pd.NA
        if isinstance(x, str):
            if x.upper() == 'A':
                return 1
            elif x.upper() == 'B':
                return 2
            else:
                try:
                    return int(x)
                except:
                    return pd.NA
        return int(x)
    df['Side'] = df['Side'].apply(side_to_int).astype('Int64')
    df['IsInitiator'] = pd.to_numeric(df['IsInitiator'], errors='coerce').astype('Int64')
    df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
    df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')
    # PolityName strip whitespace if string
    df['PolityName'] = df['PolityName'].astype('string').str.strip()
    return df

df0 = convert_types(df0)
df1 = convert_types(df1)
df2 = convert_types(df2)
df3 = convert_types(df3)

# Join df0 and df1 on WarID and PolityID
df01 = pd.merge(df0, df1, on=['WarID', 'PolityID'], how='outer', suffixes=('_0', '_1'))

# Join with df2
df012 = pd.merge(df01, df2, on=['WarID', 'PolityID'], how='outer', suffixes=('', '_2'))

# Join with df3
df_all = pd.merge(df012, df3, on=['WarID', 'PolityID'], how='outer', suffixes=('', '_3'))

# Coalesce PolityName from all sources: prefer df0, then df1, then df3, then df2
def coalesce_polityname(row):
    for col in ['PolityName_0', 'PolityName_1', 'PolityName', 'PolityName_3']:
        val = row.get(col, pd.NA)
        if pd.notna(val) and val != '':
            return val
    return pd.NA

df_all['PolityName'] = df_all.apply(coalesce_polityname, axis=1)

# For other columns, coalesce similarly or take from any source, or aggregate later
# Prepare columns for aggregation by coalescing columns from different sources

def coalesce_columns(df, col_base):
    cols = [c for c in df.columns if c == col_base or c.startswith(col_base + '_')]
    # Return row-wise first non-null value among these columns
    return df[cols].bfill(axis=1).iloc[:, 0]

# Coalesce columns needed for groupby and aggregation
df_all['StartYear'] = coalesce_columns(df_all, 'StartYear').astype('Int64')
df_all['StartMonth'] = coalesce_columns(df_all, 'StartMonth').astype('Int64')
df_all['StartDay'] = coalesce_columns(df_all, 'StartDay').astype('Int64')
df_all['EndYear'] = coalesce_columns(df_all, 'EndYear').astype('Int64')
df_all['EndMonth'] = coalesce_columns(df_all, 'EndMonth').astype('Int64')
df_all['EndDay'] = coalesce_columns(df_all, 'EndDay').astype('Int64')
df_all['Side'] = coalesce_columns(df_all, 'Side').astype('Int64')
df_all['IsInitiator'] = coalesce_columns(df_all, 'IsInitiator').astype('Int64')
df_all['Outcome'] = coalesce_columns(df_all, 'Outcome').astype('Int64')
df_all['Deaths'] = coalesce_columns(df_all, 'Deaths').astype('Int64')

# Now group by PolityName, WarID, PolityID and aggregate as per plan
agg_df = df_all.groupby(['PolityName', 'WarID', 'PolityID'], dropna=False).agg(
    StartYear=('StartYear', 'min'),
    StartMonth=('StartMonth', 'min'),
    StartDay=('StartDay', 'min'),
    EndYear=('EndYear', 'max'),
    EndMonth=('EndMonth', 'max'),
    EndDay=('EndDay', 'max'),
    Side=('Side', 'max'),
    IsInitiator=('IsInitiator', 'max'),
    Outcome=('Outcome', 'max'),
    Deaths=('Deaths', 'sum')
).reset_index()

# Convert columns to exact target types
agg_df['PolityName'] = agg_df['PolityName'].astype('string').str.strip()
agg_df['WarID'] = agg_df['WarID'].astype('Int64')
agg_df['PolityID'] = agg_df['PolityID'].astype('Int64')
agg_df['StartYear'] = agg_df['StartYear'].astype('Int64')
agg_df['StartMonth'] = agg_df['StartMonth'].astype('Int64')
agg_df['StartDay'] = agg_df['StartDay'].astype('Int64')
agg_df['EndYear'] = agg_df['EndYear'].astype('Int64')
agg_df['EndMonth'] = agg_df['EndMonth'].astype('Int64')
agg_df['EndDay'] = agg_df['EndDay'].astype('Int64')
agg_df['Side'] = agg_df['Side'].astype('Int64')
agg_df['IsInitiator'] = agg_df['IsInitiator'].astype('Int64')
agg_df['Outcome'] = agg_df['Outcome'].astype('Int64')
agg_df['Deaths'] = agg_df['Deaths'].astype('Int64')

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)