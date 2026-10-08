import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df = df0[['game_season', 'is_goal']].copy()

grouped = df.groupby(['game_season', 'is_goal'], dropna=False).size().reset_index(name='is_goal_count1')

season_sum = df.groupby('game_season', dropna=False).size().reset_index(name='season_sum')

result = pd.merge(grouped, season_sum, on='game_season', how='left')

result = result[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)