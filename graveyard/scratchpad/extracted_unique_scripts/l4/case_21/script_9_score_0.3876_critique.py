import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

grouped = df0.groupby(['game_season', 'is_goal'], dropna=False).agg(
    season_sum=pd.NamedAgg(column='is_goal', aggfunc=lambda x: x.fillna(0).sum()),
    is_goal_count1=pd.NamedAgg(column='is_goal', aggfunc='count')
).reset_index()

grouped['season_sum'] = grouped['season_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)
grouped['game_season'] = grouped['game_season'].astype(str)
grouped['is_goal'] = grouped['is_goal'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)