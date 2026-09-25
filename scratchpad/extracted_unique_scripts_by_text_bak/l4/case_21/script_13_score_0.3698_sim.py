import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

pivot = df0.groupby(['game_season', 'is_goal']).agg(
    is_goal_count1=('is_goal', 'count'),
    season_sum=('is_goal', 'sum')
).reset_index()

pivot['season_sum'] = pivot['season_sum'].fillna(0).astype(int)
pivot['is_goal_count1'] = pivot['is_goal_count1'].astype(int)
pivot['is_goal'] = pivot['is_goal'].astype(float)
pivot['game_season'] = pivot['game_season'].astype(str)

pivot = pivot[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)