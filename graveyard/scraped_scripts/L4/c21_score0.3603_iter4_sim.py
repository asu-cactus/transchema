import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df0['is_goal'] = df0['is_goal'].fillna(0.0).astype(float)
grouped = df0.groupby(['game_season', 'is_goal']).size().reset_index(name='is_goal_count1')
season_sum = df0.groupby('game_season').size().reset_index(name='season_sum')

pivot = grouped.pivot(index='game_season', columns='is_goal', values='is_goal_count1').reset_index()
pivot.columns.name = None

pivot = pivot.rename(columns={0.0: 'count_0', 1.0: 'count_1'}).fillna(0).astype({'count_0': int, 'count_1': int})

# We want to produce rows for each game_season and is_goal (0.0 and 1.0) with columns:
# game_season, is_goal (float), season_sum (int), is_goal_count1 (int)
# So we melt pivot back to long format for is_goal and is_goal_count1

df_long_0 = pivot[['game_season', 'count_0']].copy()
df_long_0['is_goal'] = 0.0
df_long_0 = df_long_0.rename(columns={'count_0': 'is_goal_count1'})

df_long_1 = pivot[['game_season', 'count_1']].copy()
df_long_1['is_goal'] = 1.0
df_long_1 = df_long_1.rename(columns={'count_1': 'is_goal_count1'})

df_long = pd.concat([df_long_0, df_long_1], ignore_index=True)

df_long = df_long.merge(season_sum, on='game_season', how='left')

df_long = df_long[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

df_long['season_sum'] = df_long['season_sum'].astype(int)
df_long['is_goal_count1'] = df_long['is_goal_count1'].astype(int)

df_long.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)