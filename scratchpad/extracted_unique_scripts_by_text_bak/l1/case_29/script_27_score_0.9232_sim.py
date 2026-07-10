import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

df_unpivot = df0[['Gender', 'Price']].copy()
df_unpivot['0'] = df_unpivot['Price'].astype(int)
df_unpivot = df_unpivot.drop(columns=['Price'])

result = df_unpivot.groupby('Gender', as_index=False)['0'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)