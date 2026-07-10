import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')
df0['area_of_shot'] = df0['area_of_shot'].astype(str)

# Compute counts per area_of_shot without reducing rows
df0['area_shot_sum'] = df0.groupby('area_of_shot')['area_of_shot'].transform('size').astype(int)
df0['is_goal_count'] = df0.groupby('area_of_shot')['is_goal'].transform('count').astype(int)

# Select only target columns in order
df_out = df0[['area_of_shot', 'is_goal', 'area_shot_sum', 'is_goal_count']]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)