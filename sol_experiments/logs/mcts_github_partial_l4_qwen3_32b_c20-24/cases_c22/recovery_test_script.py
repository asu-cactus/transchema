import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_22/test_0.csv', index_col=0)
grouped = df.groupby('type_of_combined_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_sum=('type_of_combined_shot', 'count'),
    is_goal_count1=('is_goal', 'sum')
).reset_index()
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts_recovery_test_val.csv', index=False)