import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

grouped = df0.groupby('crit_cn', as_index=False).agg({'critic': pd.Series.nunique})

grouped.columns = ['crit_cn', 'critic']

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)