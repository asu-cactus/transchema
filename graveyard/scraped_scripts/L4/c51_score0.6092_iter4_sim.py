import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

def unify_columns(df):
    cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]

df0 = unify_columns(df0)
df1 = unify_columns(df1)
df2 = unify_columns(df2)
df3 = unify_columns(df3)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['PolityName'] = pd.to_numeric(df_all['PolityName'], errors='coerce')

df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')
df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').astype('Int64')
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').astype('Int64')

df_all['Side'] = df_all['Side'].astype(str)

df_grouped = df_all.groupby('Side', dropna=False).agg({
    'WarID': 'count',
    'Deaths': 'sum',
    'Outcome': 'max',
    'IsInitiator': 'max',
    'PolityID': 'max',
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'PolityName': 'max'
}).reset_index()

df_grouped = df_grouped.rename(columns={
    'WarID': 'WarID',
    'Deaths': 'Deaths',
    'Outcome': 'Outcome',
    'IsInitiator': 'IsInitiator',
    'PolityID': 'PolityID',
    'StartYear': 'StartYear',
    'StartMonth': 'StartMonth',
    'StartDay': 'StartDay',
    'EndYear': 'EndYear',
    'EndMonth': 'EndMonth',
    'EndDay': 'EndDay',
    'PolityName': 'PolityName'
})

df_grouped = df_grouped.astype({
    'Side': 'string',
    'WarID': 'Int64',
    'PolityID': 'Int64',
    'StartYear': 'Int64',
    'StartMonth': 'Int64',
    'StartDay': 'Int64',
    'EndYear': 'Int64',
    'EndMonth': 'Int64',
    'EndDay': 'Int64',
    'IsInitiator': 'Int64',
    'Outcome': 'Int64',
    'Deaths': 'Int64',
    'PolityName': 'Int64'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)