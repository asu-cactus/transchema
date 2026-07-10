import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

unpivot_cols = ['sad.depressed', 'open.stressed']
df_unpivot = df.melt(id_vars=['user_id'], value_vars=unpivot_cols, var_name='variable', value_name='value')

df_grouped = df_unpivot.groupby(['user_id', 'variable'], as_index=False)['value'].sum()

df_pivot = df_grouped.pivot(index='user_id', columns='variable', values='value').reset_index()

df_pivot = df_pivot.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

df_pivot = df_pivot.astype({'user_id': int, 'sad': float, 'stressed': float})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)