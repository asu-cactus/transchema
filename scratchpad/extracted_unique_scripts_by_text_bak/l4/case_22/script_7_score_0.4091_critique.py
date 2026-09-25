import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

df0 = df0[df0['type_of_combined_shot'].notna()]

grouped = df0.groupby(['type_of_combined_shot', 'is_goal'], dropna=False).agg(
    shot_sum=('is_goal', 'size'),
    is_goal_count1=('is_goal', lambda x: (x == 1).sum())
).reset_index()

grouped['is_goal'] = grouped['is_goal'].astype(float)
grouped['shot_sum'] = grouped['shot_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)