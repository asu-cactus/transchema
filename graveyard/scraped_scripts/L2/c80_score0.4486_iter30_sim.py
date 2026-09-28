import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

df_pivot = df_union.melt(var_name='variable', value_name='value')
df_pivot['variable'] = df_pivot['variable'].astype(int)
df_pivot['value'] = df_pivot['value'].astype(float)

df_target = df_pivot.pivot_table(index=df_pivot.index // 4, columns='variable', values='value')
df_target.columns = df_target.columns.astype(str)
df_target = df_target[['0', '1', '2', '3']].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)