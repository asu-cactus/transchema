import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').fillna(0).astype(int)
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').fillna(0).astype(int)
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

agg_df = df.groupby('GEO.id', as_index=False).agg({
    'GEO.id2': 'max',
    'GEO.display-label': 'max',
    'HD01_VD01': 'max',
    'HD02_VD01': 'max',
    'Year': 'max'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)