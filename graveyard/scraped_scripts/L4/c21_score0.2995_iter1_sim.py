import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="game_season", suffixes=('', '_y'))

agg = joined.groupby("game_season").agg(
    is_goal=('is_goal', 'mean'),
    season_sum=('is_goal', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

agg['season_sum'] = agg['season_sum'].astype(int)
agg['is_goal_count1'] = agg['is_goal_count1'].astype(int)
agg['game_season'] = agg['game_season'].astype(str)
agg['is_goal'] = agg['is_goal'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)