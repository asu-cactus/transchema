import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

grouped = df0.groupby('type_of_combined_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    is_goal_count1=('shot_id_number', 'count'),
    shot_sum=('shot_id_number', 'sum')
).reset_index()

grouped['shot_sum'] = grouped['shot_sum'].astype('int64')
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype('int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)