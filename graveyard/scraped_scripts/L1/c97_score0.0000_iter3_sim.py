import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['crit_cn'], value_vars=['critic'], var_name='variable', value_name='critic')
df_grouped = df_unpivot.groupby('crit_cn', as_index=False)['critic'].count()
df_grouped = df_grouped.rename(columns={'critic': 'critic'})
df_grouped['critic'] = df_grouped['critic'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)