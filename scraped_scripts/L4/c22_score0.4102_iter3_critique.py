import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

df_grouped = df0.groupby(['type_of_combined_shot', 'is_goal'], dropna=False).agg(
    shot_sum=('is_goal', 'size'),
    is_goal_count1=('is_goal', 'sum')
).reset_index()

df_grouped['shot_sum'] = df_grouped['shot_sum'].astype(int)
df_grouped['is_goal_count1'] = df_grouped['is_goal_count1'].fillna(0).astype(int)
df_grouped['is_goal'] = df_grouped['is_goal'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)