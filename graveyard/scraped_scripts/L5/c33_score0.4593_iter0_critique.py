import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['GEO.id2'] = df['GEO.id2'].astype(str)

# Convert columns to numeric with nullable integer dtype
df['GEO.id'] = pd.to_numeric(df['GEO.id'], errors='coerce').astype('Int64')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

df = df[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

# Group by GEO.id2 and aggregate other columns by max to get consistent values per key
df = df.groupby('GEO.id2', as_index=False).agg({
    'GEO.id': 'max',
    'GEO.display-label': 'max',
    'HD01_VD01': 'max',
    'HD02_VD01': 'max',
    'Year': 'max'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)