import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

def ensure_polityname(df):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    return df

df0 = ensure_polityname(df0)
df1 = ensure_polityname(df1)
df2 = ensure_polityname(df2)
df3 = ensure_polityname(df3)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

df_all['PolityName'] = df_all['PolityName'].astype('string')

cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

df_all = df_all[cols]

df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').astype('Int64')
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').astype('Int64')
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').astype('Int64')
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').astype('Int64')
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').astype('Int64')

def side_to_int(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return int(x)
    if isinstance(x, str):
        if x.isdigit():
            return int(x)
        # Map letters to integers: A=1, B=2, C=3, D=4, etc.
        return ord(x.upper()) - ord('A') + 1
    return pd.NA

df_all['Side'] = df_all['Side'].apply(side_to_int).astype('Int64')
df_all['IsInitiator'] = pd.to_numeric(df_all['IsInitiator'], errors='coerce').astype('Int64')
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)