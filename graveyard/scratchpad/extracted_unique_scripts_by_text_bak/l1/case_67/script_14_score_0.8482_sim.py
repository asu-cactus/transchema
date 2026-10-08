import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['user_id'], value_vars=['sad.depressed', 'open.stressed'], var_name='emotion', value_name='value')

df_unpivot['emotion'] = df_unpivot['emotion'].map({'sad.depressed': 'sad', 'open.stressed': 'stressed'})

df_pivot = df_unpivot.pivot_table(index='user_id', columns='emotion', values='value', aggfunc='mean').reset_index()

df_pivot['sad'] = df_pivot['sad'].astype(float)
df_pivot['stressed'] = df_pivot['stressed'].astype(float)
df_pivot['user_id'] = df_pivot['user_id'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)