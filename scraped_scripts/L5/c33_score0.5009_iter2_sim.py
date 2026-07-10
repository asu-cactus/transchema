import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df_all['GEO.id'] = pd.to_numeric(df_all['GEO.id'], errors='coerce').fillna(0).astype(int)
df_all['GEO.display-label'] = pd.to_numeric(df_all['GEO.display-label'], errors='coerce').fillna(0).astype(int)
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce').fillna(0).astype(int)
df_all['GEO.id2'] = df_all['GEO.id2'].astype(str)

grouped = df_all.groupby(['GEO.id2', 'GEO.id', 'GEO.display-label', 'Year'], dropna=False, as_index=False).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

grouped = grouped[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)