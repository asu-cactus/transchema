import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

grouped = df0.groupby('game_season').agg(
    is_goal=('is_goal', 'mean'),
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

grouped['season_sum'] = grouped['season_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)
grouped['game_season'] = grouped['game_season'].astype(str)
grouped['is_goal'] = grouped['is_goal'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)