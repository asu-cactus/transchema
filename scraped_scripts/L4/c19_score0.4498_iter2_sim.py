import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

# The partial plan suggests a join of Source4_19_0 with itself on shot_basics and area_of_shot.
# But joining the same table on these columns is unusual and likely not needed for the target schema.
# Instead, we interpret the hint as focusing on shot_basics and area_of_shot columns for aggregation.

# Since the target schema is:
# ['shot_basics': string, 'is_goal': float, 'shot_basics_sum': integer, 'is_goal_count1': integer]
# and target examples show shot_basics, is_goal (float), shot_basics_sum (int), is_goal_count1 (int),
# we need to group by shot_basics and aggregate is_goal (mean or sum?), shot_basics_sum (sum of counts?), is_goal_count1 (count of is_goal=1?).

# From the example:
# shot_basics_sum looks like a sum of counts of shot_basics occurrences
# is_goal_count1 looks like count of is_goal=1 occurrences per shot_basics
# is_goal is float, likely mean or sum of is_goal per shot_basics (target examples show 0.0, so likely mean or sum)

# Let's do:
# Group by shot_basics
# shot_basics_sum = count of rows per shot_basics
# is_goal_count1 = count of rows where is_goal == 1 per shot_basics
# is_goal = mean of is_goal per shot_basics (NaNs ignored)

df = df0[['shot_basics', 'is_goal']].copy()

# Clean shot_basics: convert to string and strip spaces
df['shot_basics'] = df['shot_basics'].astype(str).str.strip()

# Convert is_goal to float (already float), keep NaNs
df['is_goal'] = pd.to_numeric(df['is_goal'], errors='coerce')

# shot_basics_sum: count of rows per shot_basics
shot_basics_sum = df.groupby('shot_basics').size().rename('shot_basics_sum')

# is_goal_count1: count of rows where is_goal == 1 per shot_basics
is_goal_count1 = df[df['is_goal'] == 1].groupby('shot_basics').size().rename('is_goal_count1')

# is_goal: mean of is_goal per shot_basics
is_goal_mean = df.groupby('shot_basics')['is_goal'].mean().rename('is_goal')

# Combine all
result = pd.concat([is_goal_mean, shot_basics_sum, is_goal_count1], axis=1).reset_index()

# Fill NaN in is_goal_count1 with 0 and convert to int
result['is_goal_count1'] = result['is_goal_count1'].fillna(0).astype(int)

# shot_basics_sum is count, convert to int
result['shot_basics_sum'] = result['shot_basics_sum'].astype(int)

# Ensure is_goal is float
result['is_goal'] = result['is_goal'].astype(float)

# Reorder columns as target schema
result = result[['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)