import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

df = df[['shot_basics', 'is_goal']].copy()

df = df.dropna(subset=['shot_basics'])

df['is_goal'] = df['is_goal'].fillna(0)

grouped = df.groupby(['shot_basics', 'is_goal']).agg(
    shot_basics_sum=('shot_basics', 'size'),
    is_goal_count1=('is_goal', 'sum')
).reset_index()

grouped['shot_basics_sum'] = grouped['shot_basics_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)