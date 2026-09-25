import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_20/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')
df0['distance_of_shot'] = pd.to_numeric(df0['distance_of_shot'], errors='coerce')

grouped = df0.groupby('range_of_shot').agg(
    is_goal=('is_goal', 'mean'),
    range_sum=('distance_of_shot', 'sum'),
    is_goal_count1=('is_goal', lambda x: x.eq(1).sum())
).reset_index()

grouped['range_sum'] = grouped['range_sum'].fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_20/target_multisource_mcts.csv", index=False)