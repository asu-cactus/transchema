import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv", index_col=0)

join01 = pd.merge(df0, df1, on="WarID", suffixes=('_0', '_1'))
join012 = pd.merge(join01, df2, on="WarID", suffixes=('', '_2'))
join0123 = pd.merge(join012, df3, on="WarID", suffixes=('', '_3'))
join01234 = pd.merge(join0123, df4, on="WarID", suffixes=('', '_4'))

def coalesce_columns(df, base_col):
    cols = [c for c in df.columns if c == base_col or c.startswith(base_col + '_')]
    for c in cols:
        if df[c].notna().any():
            first_non_na = c
            break
    else:
        return pd.Series([pd.NA]*len(df))
    result = df[first_non_na].copy()
    for c in cols:
        if c == first_non_na:
            continue
        result = result.combine_first(df[c])
    return result

result = pd.DataFrame()
result['Initiator'] = coalesce_columns(join01234, 'Initiator')
result['WarID'] = join01234['WarID']
result['PolityName'] = coalesce_columns(join01234, 'PolityName')
result['StartYear'] = coalesce_columns(join01234, 'StartYear').astype('Int64')
result['StartMonth'] = coalesce_columns(join01234, 'StartMonth').astype('Int64')
result['StartDay'] = coalesce_columns(join01234, 'StartDay').astype('Int64')
result['EndYear'] = coalesce_columns(join01234, 'EndYear').astype('Int64')
result['EndMonth'] = coalesce_columns(join01234, 'EndMonth').astype('Int64')
result['EndDay'] = coalesce_columns(join01234, 'EndDay').astype('Int64')
result['Outcome'] = coalesce_columns(join01234, 'Outcome').astype('Int64')
result['Deaths'] = coalesce_columns(join01234, 'Deaths').astype('Int64')

grouped = result.groupby('Initiator', dropna=False).agg({
    'WarID': 'first',
    'PolityName': 'first',
    'StartYear': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Outcome': 'first',
    'Deaths': 'first'
}).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)