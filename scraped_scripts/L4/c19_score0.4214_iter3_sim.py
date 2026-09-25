import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df0 = df0[['shot_basics', 'is_goal']].copy()
df0 = df0.dropna(subset=['shot_basics'])

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

grouped = df0.groupby('shot_basics', dropna=False)

shot_basics_sum = grouped.size()
is_goal_sum = grouped['is_goal'].sum(min_count=1)
is_goal_count1 = grouped['is_goal'].count()

result = pd.DataFrame({
    'shot_basics': shot_basics_sum.index,
    'is_goal': is_goal_sum / is_goal_count1,
    'shot_basics_sum': shot_basics_sum.values,
    'is_goal_count1': is_goal_count1.values
})

result['is_goal'] = result['is_goal'].fillna(0.0)
result['shot_basics_sum'] = result['shot_basics_sum'].astype(int)
result['is_goal_count1'] = result['is_goal_count1'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)