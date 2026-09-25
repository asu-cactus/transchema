import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_1.csv", index_col=0)

df1_unpivot = df1[['Store', 'StoreType']].copy()
df1_unpivot = df1_unpivot.rename(columns={'StoreType': 'StoreType', 'Store': 'Store'})

df1_unpivot['Store'] = df1_unpivot['Store'].astype(int)
df1_unpivot['StoreType'] = df1_unpivot['StoreType'].astype(str)

df1_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length2_42/target_multisource_mcts.csv", index=False)