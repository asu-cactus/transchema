import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

agg = df0.groupby(['crit_cn', 'critic'], as_index=False).agg({'movie':'count'})

result = agg.rename(columns={'crit_cn':'crit_cn', 'critic':'critic'})

result = result[['crit_cn', 'critic']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)