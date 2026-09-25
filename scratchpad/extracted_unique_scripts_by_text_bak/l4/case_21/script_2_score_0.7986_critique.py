import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

agg = df0.groupby('game_season').agg(
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

result = pd.merge(df0[['game_season', 'is_goal']], agg, on='game_season', how='left')

result['game_season'] = result['game_season'].astype(str)
result['is_goal'] = result['is_goal'].astype(float)
result['season_sum'] = result['season_sum'].fillna(0).astype(int)
result['is_goal_count1'] = result['is_goal_count1'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)