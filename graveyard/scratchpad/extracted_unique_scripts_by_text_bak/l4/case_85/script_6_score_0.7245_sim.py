import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

df_unpivot = df0[['crit_cn', 'critic']]

result = df_unpivot.groupby('crit_cn', as_index=False)['critic'].count()
result.columns = ['crit_cn', 'critic']

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)