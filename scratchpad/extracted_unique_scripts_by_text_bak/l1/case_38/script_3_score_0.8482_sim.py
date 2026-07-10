import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df_unpivot = df.melt(id_vars=['user_id'], value_vars=['sad.depressed', 'open.stressed'], var_name='emotion', value_name='score')

df_pivot = df_unpivot.pivot_table(index='user_id', columns='emotion', values='score', aggfunc='mean').reset_index()

df_pivot = df_pivot.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)