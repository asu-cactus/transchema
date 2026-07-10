import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby(
    ['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD02_VD01', 'Year'], dropna=False, as_index=False
).agg({'HD01_VD01': 'sum'})

df_grouped['GEO.id'] = df_grouped['GEO.id'].astype(str)
df_grouped['GEO.id2'] = pd.to_numeric(df_grouped['GEO.id2'], errors='coerce').astype('Int64')
df_grouped['GEO.display-label'] = pd.to_numeric(df_grouped['GEO.display-label'], errors='coerce').astype('Int64')
df_grouped['HD01_VD01'] = pd.to_numeric(df_grouped['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_grouped['HD02_VD01'] = pd.to_numeric(df_grouped['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df_grouped['Year'] = pd.to_numeric(df_grouped['Year'], errors='coerce').astype('Int64')

df_grouped.to_csv(
    "autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv",
    index=False
)