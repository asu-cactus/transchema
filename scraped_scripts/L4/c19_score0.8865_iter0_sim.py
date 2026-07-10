import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

grouped = df0.groupby('shot_basics', dropna=False).agg(
    shot_basics_sum=('shot_basics', 'size'),
    is_goal_count1=('is_goal', 'count'),
    is_goal_sum=('is_goal', 'sum')
).reset_index()

grouped['is_goal'] = grouped['is_goal_sum']  # float
grouped['shot_basics_sum'] = grouped['shot_basics_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

result = df0[['shot_basics', 'is_goal']].merge(
    grouped[['shot_basics', 'shot_basics_sum', 'is_goal_count1']],
    on='shot_basics',
    how='left'
)

result = result[['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)