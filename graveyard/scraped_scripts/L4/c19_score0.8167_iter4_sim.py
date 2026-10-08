import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df = df[['shot_basics', 'is_goal']].copy()

df_unpivot = df.dropna(subset=['shot_basics'])
df_unpivot['is_goal'] = df_unpivot['is_goal'].fillna(0)

grouped = df_unpivot.groupby('shot_basics').agg(
    shot_basics_sum=('shot_basics', 'size'),
    is_goal_count1=('is_goal', 'sum')
).reset_index()

grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)
grouped['shot_basics_sum'] = grouped['shot_basics_sum'].astype(int)

df_goal = df_unpivot[df_unpivot['is_goal'] == 1].copy()
df_nongoal = df_unpivot[df_unpivot['is_goal'] == 0].copy()

df_goal = df_goal.merge(grouped, on='shot_basics', how='left')
df_nongoal = df_nongoal.merge(grouped, on='shot_basics', how='left')

result = pd.concat([df_goal, df_nongoal], ignore_index=True)

result = result[['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)