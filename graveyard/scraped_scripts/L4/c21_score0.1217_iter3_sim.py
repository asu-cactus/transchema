import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on=['game_season', 'is_goal'], how='inner', suffixes=('', '_y'))

grouped = joined.groupby('game_season', dropna=False).agg(
    season_sum=pd.NamedAgg(column='is_goal', aggfunc='sum'),
    is_goal_count1=pd.NamedAgg(column='is_goal', aggfunc='count')
).reset_index()

grouped['is_goal'] = pd.NA
grouped['season_sum'] = grouped['season_sum'].fillna(0).astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].fillna(0).astype(int)
grouped['game_season'] = grouped['game_season'].astype(str)

result = grouped[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)