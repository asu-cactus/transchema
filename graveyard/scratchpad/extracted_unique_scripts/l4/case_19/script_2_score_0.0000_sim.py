import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

grouped = df0.groupby('shot_basics', dropna=False).agg(
    is_goal_sum=('is_goal', 'sum'),
    shot_basics_count=('shot_basics', 'count'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

grouped['is_goal'] = grouped['is_goal_sum'] / grouped['shot_basics_count']
grouped['shot_basics_sum'] = grouped['shot_basics_count']

result = grouped[['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)