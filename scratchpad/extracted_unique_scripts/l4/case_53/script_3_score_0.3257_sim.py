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
df3 = ensure_polityname(df3)
df2 = ensure_polityname(df2)

common_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

df0 = df0[common_cols]
df1 = df1[common_cols]
df2 = df2[common_cols]
df3 = df3[common_cols]

df_all_1 = pd.concat([df0, df1, df3], ignore_index=True)
df_all = pd.concat([df_all_1, df2], ignore_index=True)

df_all['PolityName'] = df_all['PolityName'].astype('string')

int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)