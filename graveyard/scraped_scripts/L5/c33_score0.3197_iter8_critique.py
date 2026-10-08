import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df_grouped = df.groupby(['GEO.id2', 'GEO.id', 'GEO.display-label'], as_index=False).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum',
    'Year': 'sum'
})

df_grouped['GEO.id2'] = df_grouped['GEO.id2'].astype(str)
df_grouped['GEO.id'] = pd.to_numeric(df_grouped['GEO.id'], errors='coerce').astype('Int64')
df_grouped['GEO.display-label'] = pd.to_numeric(df_grouped['GEO.display-label'], errors='coerce').astype('Int64')
df_grouped['HD01_VD01'] = pd.to_numeric(df_grouped['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_grouped['HD02_VD01'] = pd.to_numeric(df_grouped['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df_grouped['Year'] = pd.to_numeric(df_grouped['Year'], errors='coerce').fillna(0).astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)