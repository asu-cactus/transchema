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

df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = df['GEO.id2'].astype(str)
df['GEO.display-label'] = df['GEO.display-label'].astype(str)

grouped = df.groupby(
    ['Year', 'HD02_VD01', 'GEO.id2', 'GEO.id', 'GEO.display-label'], dropna=False,
    as_index=False
).agg({'HD01_VD01': 'sum'})

grouped['GEO.id'] = grouped['GEO.id'].apply(lambda x: int(x) if x.isdigit() else 0)
grouped['GEO.display-label'] = grouped['GEO.display-label'].apply(lambda x: int(x) if str(x).isdigit() else 0)
grouped['HD01_VD01'] = grouped['HD01_VD01'].fillna(0).astype(int)
grouped['HD02_VD01'] = grouped['HD02_VD01'].fillna(0).astype(int)
grouped['Year'] = grouped['Year'].fillna(0).astype(int)

grouped = grouped[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)