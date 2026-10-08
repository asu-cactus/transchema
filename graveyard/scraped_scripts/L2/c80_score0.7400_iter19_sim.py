import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)
df_unpivot = df0.melt(var_name='variable', value_name='value')
df_unpivot['variable'] = df_unpivot['variable'].astype(float)
df_unpivot['value'] = df_unpivot['value'].astype(float)
df_unpivot = df_unpivot.rename(columns={'variable': '1', 'value': '0'})
df_unpivot['2'] = 0.0
df_unpivot['3'] = 0.0
df_unpivot = df_unpivot[['0', '1', '2', '3']]
df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)