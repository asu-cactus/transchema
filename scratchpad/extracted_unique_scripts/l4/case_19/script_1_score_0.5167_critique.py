import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

grouped = df0.groupby('shot_basics', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_basics_sum=('shot_basics', 'count'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)