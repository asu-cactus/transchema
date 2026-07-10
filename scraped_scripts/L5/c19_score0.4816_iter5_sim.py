import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce').fillna(0).astype(int)
df_all['GEO.id2'] = pd.to_numeric(df_all['GEO.id2'], errors='coerce').fillna(0).astype(int)

grouped = df_all.groupby(
    ['GEO.display-label', 'GEO.id', 'GEO.id2', 'Year'], dropna=False, as_index=False
).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

grouped = grouped.astype({
    'GEO.display-label': str,
    'GEO.id': str,
    'GEO.id2': int,
    'HD01_VD01': int,
    'HD02_VD01': int,
    'Year': int
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)