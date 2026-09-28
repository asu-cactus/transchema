import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

grouped = df0.groupby(['game_season', 'is_goal'], dropna=False).agg(
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

grouped['is_goal'] = grouped['is_goal'].astype(float)
grouped['season_sum'] = grouped['season_sum'].fillna(0).astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped = grouped[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)