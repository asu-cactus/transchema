import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_61/training_0.csv", index_col=0)

df_pivot = df0.melt(var_name="variable", value_name="value")
df_pivot['variable'] = df_pivot['variable'].astype(int)
df_pivot = df_pivot.pivot_table(index=df_pivot.index, columns='variable', values='value')
df_pivot.columns = df_pivot.columns.astype(str)
df_pivot = df_pivot[['0', '1', '2', '3']]
df_pivot = df_pivot.astype(float)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length2_61/target_multisource_mcts.csv")