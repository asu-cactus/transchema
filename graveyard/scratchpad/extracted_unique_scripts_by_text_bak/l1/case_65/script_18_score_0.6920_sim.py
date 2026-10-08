import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_unpivot = df[['year']].copy()
df_unpivot['0'] = 1
result = df_unpivot.groupby('year', as_index=False)['0'].sum()
result['year'] = result['year'].astype(int)
result['0'] = result['0'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)