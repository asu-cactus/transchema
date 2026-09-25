import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

grouped = df0.groupby('area_of_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    area_shot_sum=('is_goal', 'sum'),
    is_goal_count=('match_event_id', 'count')
).reset_index()

grouped['area_shot_sum'] = grouped['area_shot_sum'].astype('Int64')
grouped['is_goal_count'] = grouped['is_goal_count'].astype('Int64')
grouped['area_of_shot'] = grouped['area_of_shot'].astype(str)

grouped = grouped[['area_of_shot', 'is_goal', 'area_shot_sum', 'is_goal_count']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)