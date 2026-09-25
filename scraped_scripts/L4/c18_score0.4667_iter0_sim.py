import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')
df0['area_of_shot'] = df0['area_of_shot'].astype(str)

grouped = df0.groupby('area_of_shot').agg(
    is_goal=('is_goal', 'mean'),
    area_shot_sum=('area_of_shot', 'size'),
    is_goal_count=('is_goal', 'count')
).reset_index()

grouped['area_shot_sum'] = grouped['area_shot_sum'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)