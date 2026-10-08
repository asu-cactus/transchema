import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

def unify_columns(df):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    df = df[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]
    return df

df0 = unify_columns(df0)
df1 = unify_columns(df1)
df2 = unify_columns(df2)
df3 = unify_columns(df3)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').fillna(0).astype(int)
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').fillna(0).astype(int)
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').fillna(0).astype(int)
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').fillna(0).astype(int)

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

df = df[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)