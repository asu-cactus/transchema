import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

agg = df0.groupby('crit_cn', as_index=False).agg({'critic':'count'})

agg = agg.rename(columns={'critic':'critic'})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)