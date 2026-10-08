import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').astype('Int64')
df['GEO.display-label'] = df['GEO.display-label'].astype(str)
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)