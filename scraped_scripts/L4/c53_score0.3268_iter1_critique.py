import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

def unify_columns(df):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    # Map Side 'A'->1, 'B'->2 if Side is object
    if df['Side'].dtype == object:
        df['Side'] = df['Side'].map({'A':1, 'B':2}).fillna(df['Side'])
    # Convert columns to target types
    df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
    df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
    df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
    df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
    df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
    df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
    df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
    df['Side'] = pd.to_numeric(df['Side'], errors='coerce').astype('Int64')
    df['IsInitiator'] = pd.to_numeric(df['IsInitiator'], errors='coerce').astype('Int64')
    df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
    df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')
    df['PolityName'] = df['PolityName'].astype('string')
    return df[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

df0u = unify_columns(df0)
df1u = unify_columns(df1)
df2u = unify_columns(df2)
df3u = unify_columns(df3)

# UNION all
df_all = pd.concat([df0u, df1u, df2u, df3u], ignore_index=True)

# GROUP BY all leftmost columns except Deaths, aggregate Deaths by sum
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

result = df_all.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths':'sum'})

# Ensure Deaths is Int64 (sum may produce int64)
result['Deaths'] = result['Deaths'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)