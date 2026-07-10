import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

grouped = df0.groupby('type_of_combined_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_sum=('shot_id_number', 'sum'),
    is_goal_count1=('is_goal', 'sum')
).reset_index()

grouped['type_of_combined_shot'] = grouped['type_of_combined_shot'].astype(str)
grouped['is_goal'] = grouped['is_goal'].astype(float)
grouped['shot_sum'] = grouped['shot_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)