import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

df_unpivot = df0[['Gender']].copy()
df_unpivot['0'] = 1
df_grouped = df_unpivot.groupby('Gender', as_index=False).agg({'0': 'sum'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)