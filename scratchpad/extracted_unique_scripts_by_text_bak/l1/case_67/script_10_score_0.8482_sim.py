import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

unpivot_cols = ['sad.depressed', 'open.stressed']
df_unpivot = df.melt(id_vars=['user_id'], value_vars=unpivot_cols, var_name='emotion', value_name='value')

df_grouped = df_unpivot.groupby(['user_id', 'emotion'], as_index=False)['value'].mean()

df_pivot = df_grouped.pivot(index='user_id', columns='emotion', values='value').reset_index()

df_pivot = df_pivot.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

df_pivot['sad'] = df_pivot['sad'].astype(float)
df_pivot['stressed'] = df_pivot['stressed'].astype(float)
df_pivot['user_id'] = df_pivot['user_id'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)