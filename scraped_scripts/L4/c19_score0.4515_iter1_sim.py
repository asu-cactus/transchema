import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

# The partial plan suggests a self-join on shot_basics, but joining a table to itself on the same column without additional keys is redundant.
# Instead, we interpret the plan as grouping by 'shot_basics' to aggregate the required columns.

# Group by 'shot_basics' and aggregate:
# - is_goal: mean (float)
# - shot_basics_sum: sum of counts of shot_basics (count of rows per shot_basics)
# - is_goal_count1: count of is_goal (integer count of non-null is_goal per shot_basics)

grouped = df0.groupby('shot_basics', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_basics_sum=('shot_basics', 'count'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

# Convert shot_basics to string type (as target schema requires string)
grouped['shot_basics'] = grouped['shot_basics'].astype(str)

# shot_basics_sum should be integer
grouped['shot_basics_sum'] = grouped['shot_basics_sum'].astype(int)

# is_goal_count1 should be integer
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)