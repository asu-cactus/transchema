import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Convert columns to consistent types for join keys
for df in [df0, df1, df2, df3]:
    df['Side'] = df['Side'].astype(str)
    df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')

# Join df0 and df1 on ['Side', 'WarID', 'PolityID']
df01 = pd.merge(df0, df1, on=['Side', 'WarID', 'PolityID'], how='inner', suffixes=('_0', '_1'))

# Join df01 and df2 on ['Side', 'WarID', 'PolityID']
df012 = pd.merge(df01, df2, on=['Side', 'WarID', 'PolityID'], how='inner', suffixes=('', '_2'))

# Join df012 and df3 on ['Side', 'WarID', 'PolityID']
df_all = pd.merge(df012, df3, on=['Side', 'WarID', 'PolityID'], how='inner', suffixes=('', '_3'))

# Now select and unify columns to match target schema:
# Target schema: ['Side': string, 'WarID': integer, 'PolityID': integer, 'StartYear': integer, 'StartMonth': integer, 'StartDay': integer, 'EndYear': integer, 'EndMonth': integer, 'EndDay': integer, 'IsInitiator': integer, 'Outcome': integer, 'Deaths': integer, 'PolityName': integer]

# The source columns are duplicated due to joins, so we must pick the correct columns from each source.
# From source0: PolityName_0 (string), StartYear_0, StartMonth_0, StartDay_0, EndYear_0, EndMonth_0, EndDay_0, IsInitiator_0, Outcome_0, Deaths_0
# From source1: no PolityName, but StartYear_1, StartMonth_1, etc.
# From source2: PolityName (string), StartYear, etc.
# From source3: PolityName (string), StartYear, etc.

# The target examples have PolityName as integer, so convert PolityName from source0,2,3 to numeric and pick one (e.g., from source0 if available, else source2, else source3)
# For other columns, pick from source0 if available, else source1, else source2, else source3

def to_int64(series):
    return pd.to_numeric(series, errors='coerce').astype('Int64')

# Prepare PolityName column: try source0 first, then source2, then source3
df_all['PolityName'] = to_int64(df_all.get('PolityName_0', pd.Series(pd.NA)))
df_all.loc[df_all['PolityName'].isna(), 'PolityName'] = to_int64(df_all.loc[df_all['PolityName'].isna(), 'PolityName'])
df_all.loc[df_all['PolityName'].isna(), 'PolityName'] = to_int64(df_all.loc[df_all['PolityName'].isna(), 'PolityName_3'])

# For other columns, prefer source0 columns if present, else source1, else source2, else source3
def coalesce_columns(df, col_base):
    # Try columns in order of preference
    for suffix in ['_0', '_1', '', '_3']:
        col = col_base + suffix
        if col in df.columns:
            return df[col]
    # If none found, return NA
    return pd.Series(pd.NA, index=df.index)

result = pd.DataFrame({
    'Side': df_all['Side'],
    'WarID': df_all['WarID'],
    'PolityID': df_all['PolityID'],
    'StartYear': to_int64(coalesce_columns(df_all, 'StartYear')),
    'StartMonth': to_int64(coalesce_columns(df_all, 'StartMonth')),
    'StartDay': to_int64(coalesce_columns(df_all, 'StartDay')),
    'EndYear': to_int64(coalesce_columns(df_all, 'EndYear')),
    'EndMonth': to_int64(coalesce_columns(df_all, 'EndMonth')),
    'EndDay': to_int64(coalesce_columns(df_all, 'EndDay')),
    'IsInitiator': to_int64(coalesce_columns(df_all, 'IsInitiator')),
    'Outcome': to_int64(coalesce_columns(df_all, 'Outcome')),
    'Deaths': to_int64(coalesce_columns(df_all, 'Deaths')),
    'PolityName': df_all['PolityName']
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)