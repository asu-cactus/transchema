import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

agg = df0.groupby(['crit_cn', 'critic'], as_index=False).agg({'movie':'count'})
agg = agg.rename(columns={'crit_cn':'crit_cn', 'critic':'critic', 'movie':'critic_count'})

# The target schema is ['crit_cn': string, 'critic': integer]
# The target examples show only crit_cn and critic columns, no count column.
# The partial plan suggests grouping by crit_cn and critic, counting movies, but target schema does not have count.
# So we just need to produce distinct pairs of crit_cn and critic.
# The groupby with count is a way to get unique pairs, but we only keep crit_cn and critic columns.

result = agg[['crit_cn', 'critic']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)