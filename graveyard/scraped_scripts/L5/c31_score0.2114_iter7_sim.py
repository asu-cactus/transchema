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

df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').astype('Int64')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')

agg_df = df.groupby(['GEO.id', 'GEO.id2', 'GEO.display-label', 'Year'], dropna=False, as_index=False).agg({
    'HD01_VD01': 'min',
    'HD02_VD01': 'min'
})

agg_df = agg_df.astype({
    'GEO.id': 'string',
    'GEO.id2': 'Int64',
    'GEO.display-label': 'Int64',
    'HD01_VD01': 'Int64',
    'HD02_VD01': 'Int64',
    'Year': 'Int64'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)