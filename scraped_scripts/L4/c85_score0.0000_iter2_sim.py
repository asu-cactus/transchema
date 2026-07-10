import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

df_grouped = df0.groupby('crit_cn', as_index=False)['critic'].sum()
df_grouped['critic'] = df_grouped['critic'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)