import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

joined = pd.merge(df, df, on=["type_of_combined_shot", "is_goal"], how="inner", suffixes=('', '_y'))

grouped = joined.groupby("type_of_combined_shot").agg(
    is_goal=('is_goal', 'sum'),
    shot_sum=('type_of_combined_shot', 'count'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

grouped['is_goal'] = grouped['is_goal'].astype(float)
grouped['shot_sum'] = grouped['shot_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)