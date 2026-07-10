import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

df0['PolityID'] = df0['PolityID'].astype('Int64')
df1['PolityID'] = df1['PolityID'].astype('Int64')
df2['PolityID'] = df2['PolityID'].astype('Int64')
df3['PolityID'] = df3['PolityID'].astype('Int64')

join_cols = ['WarID', 'PolityID']

df_join = pd.merge(df0, df1, on=join_cols, how='outer', suffixes=('_0', '_1'))

def coalesce_columns(df, col0, col1):
    if col0 in df.columns and col1 in df.columns:
        return df[col0].combine_first(df[col1])
    elif col0 in df.columns:
        return df[col0]
    elif col1 in df.columns:
        return df[col1]
    else:
        return pd.Series([pd.NA]*len(df))

df_join['PolityName'] = coalesce_columns(df_join, 'PolityName_0', 'PolityName_1')

for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']:
    df_join[col] = coalesce_columns(df_join, f"{col}_0", f"{col}_1")

df_join = df_join[join_cols + ['PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

df_join['Side'] = df_join['Side'].replace({'A':1, 'B':2}).astype('Int64')
df_join['IsInitiator'] = df_join['IsInitiator'].astype('Int64')
df_join['Outcome'] = df_join['Outcome'].astype('Int64')
df_join['Deaths'] = df_join['Deaths'].astype('Int64')

df2['Side'] = df2['Side'].replace({'A':1, 'B':2}).astype('Int64')
df2['IsInitiator'] = df2['IsInitiator'].astype('Int64')
df2['Outcome'] = df2['Outcome'].astype('Int64')
df2['Deaths'] = df2['Deaths'].astype('Int64')

df3['Side'] = df3['Side'].replace({'A':1, 'B':2}).astype('Int64')
df3['IsInitiator'] = df3['IsInitiator'].astype('Int64')
df3['Outcome'] = df3['Outcome'].astype('Int64')
df3['Deaths'] = df3['Deaths'].astype('Int64')

df3['PolityName'] = df3['PolityName'].astype('string')

df_all = pd.concat([df_join, df2, df3], ignore_index=True, sort=False)

df_all = df_all[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

df_all['PolityName'] = df_all['PolityName'].astype('string')
df_all['WarID'] = df_all['WarID'].astype('Int64')
df_all['PolityID'] = df_all['PolityID'].astype('Int64')
df_all['StartYear'] = df_all['StartYear'].astype('Int64')
df_all['StartMonth'] = df_all['StartMonth'].astype('Int64')
df_all['StartDay'] = df_all['StartDay'].astype('Int64')
df_all['EndYear'] = df_all['EndYear'].astype('Int64')
df_all['EndMonth'] = df_all['EndMonth'].astype('Int64')
df_all['EndDay'] = df_all['EndDay'].astype('Int64')
df_all['Side'] = df_all['Side'].astype('Int64')
df_all['IsInitiator'] = df_all['IsInitiator'].astype('Int64')
df_all['Outcome'] = df_all['Outcome'].astype('Int64')
df_all['Deaths'] = df_all['Deaths'].astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)