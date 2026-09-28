import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = df['GEO.id2'].astype(str)
df['GEO.display-label'] = df['GEO.display-label'].astype(str)
df['HD01_VD01'] = df['HD01_VD01'].astype(str)
df['HD02_VD01'] = df['HD02_VD01'].astype(str)
df['Year'] = df['Year'].astype(int)

df = df[['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_70/target_multisource_mcts.csv", index=False)