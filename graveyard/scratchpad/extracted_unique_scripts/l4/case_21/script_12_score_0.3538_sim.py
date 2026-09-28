import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df_unpivot = df[['game_season', 'is_goal']].copy()
df_unpivot['is_goal'] = pd.to_numeric(df_unpivot['is_goal'], errors='coerce')

grouped = df_unpivot.groupby(['game_season', 'is_goal'], dropna=False).size().reset_index(name='is_goal_count1')

season_sum = df_unpivot.groupby('game_season', dropna=False)['is_goal'].sum().reset_index(name='season_sum')

result = pd.merge(grouped, season_sum, on='game_season', how='left')

result['season_sum'] = result['season_sum'].fillna(0).astype(int)
result['is_goal_count1'] = result['is_goal_count1'].fillna(0).astype(int)
result['is_goal'] = result['is_goal'].astype(float)
result['game_season'] = result['game_season'].astype(str)

result = result[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)