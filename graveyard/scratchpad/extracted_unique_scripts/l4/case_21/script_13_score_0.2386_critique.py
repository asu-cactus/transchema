import pandas as pd

# Read the single source file (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

# If there were multiple source tables, we would read and union them here.
# Since only one source is given, union is trivial.

# Select relevant columns and convert is_goal to numeric
df = df0[['game_season', 'is_goal']].copy()
df['is_goal'] = pd.to_numeric(df['is_goal'], errors='coerce')

# Replace NaN in is_goal with 0 for sum aggregation
df['is_goal'] = df['is_goal'].fillna(0)

# Group by game_season and aggregate
result = df.groupby('game_season', dropna=False).agg(
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

# Cast types to match target schema
result['season_sum'] = result['season_sum'].astype(int)
result['is_goal_count1'] = result['is_goal_count1'].astype(int)
result['game_season'] = result['game_season'].astype(str)

# The target schema is ['game_season': string, 'is_goal': float, 'season_sum': integer, 'is_goal_count1': integer]
# The 'is_goal' column in target is float but in examples it contains NaN or 0/1 values.
# Since we aggregated sum and count, we need to add 'is_goal' column as float with NaN values (or keep as NaN).
# The target examples show 'is_goal' as NaN or 0.0 or 1.0, but since we aggregated by season only,
# we cannot produce per-row is_goal values. The best is to set 'is_goal' column as NaN for all rows.

result['is_goal'] = float('nan')

# Reorder columns to match target schema
result = result[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)