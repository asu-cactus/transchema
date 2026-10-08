import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

# Use a sentinel value for NaN in is_goal to include them in groupby
df0['is_goal_filled'] = df0['is_goal'].fillna(-1)

agg = df0.groupby(['game_season', 'is_goal_filled']).agg(
    season_sum=('is_goal', lambda x: x.fillna(0).sum()),
    is_goal_count1=('match_event_id', 'count')
).reset_index()

# Restore NaN in is_goal where sentinel -1 was used
agg['is_goal'] = agg['is_goal_filled'].replace(-1, np.nan)

# Cast columns to correct types
agg['season_sum'] = agg['season_sum'].astype(int)
agg['is_goal_count1'] = agg['is_goal_count1'].astype(int)
agg['game_season'] = agg['game_season'].astype(str)
agg['is_goal'] = agg['is_goal'].astype(float)

# Select columns in target schema order
agg = agg[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)