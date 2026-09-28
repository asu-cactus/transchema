import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df[['GEO.display-label', 'GEO.id', 'GEO.id2', 'HD01_VD01', 'HD02_VD01', 'Year']]

df['GEO.id'] = df['GEO.id'].astype(int, errors='ignore')
df['GEO.id2'] = df['GEO.id2'].astype(int, errors='ignore')
df['HD01_VD01'] = df['HD01_VD01'].astype(int, errors='ignore')
df['HD02_VD01'] = df['HD02_VD01'].astype(int, errors='ignore')
df['Year'] = df['Year'].astype(int, errors='ignore')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)