import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

# The partial plan suggests a join of Source4_21_0 with itself on game_season.
# This join is redundant because it's the same table joined on the same column,
# so it will produce a Cartesian product per game_season.
# Instead, we can directly group by game_season and aggregate.

# Prepare is_goal as float (already float or NaN)
df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

# Group by game_season to get season_sum and is_goal_count1
agg = df0.groupby('game_season').agg(
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

# The target table also has columns: game_season (string), is_goal (float), season_sum (int), is_goal_count1 (int)
# The 'is_goal' column in target is per-row, so we keep it from original df0.
# Merge original df0 with agg on game_season to get season_sum and is_goal_count1 columns
result = pd.merge(df0[['game_season', 'is_goal']], agg, on='game_season', how='left')

# Convert types to match target schema
result['game_season'] = result['game_season'].astype(str)
result['is_goal'] = result['is_goal'].astype(float)
result['season_sum'] = result['season_sum'].fillna(0).astype(int)
result['is_goal_count1'] = result['is_goal_count1'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)