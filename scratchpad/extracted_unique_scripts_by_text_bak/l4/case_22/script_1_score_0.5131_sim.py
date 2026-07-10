import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

df = df0[['type_of_combined_shot', 'is_goal']].copy()

agg = df.groupby('type_of_combined_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_sum=('is_goal', 'size'),
    is_goal_count1=('is_goal', lambda x: (x == 1).sum())
).reset_index()

agg['shot_sum'] = agg['shot_sum'].astype(int)
agg['is_goal_count1'] = agg['is_goal_count1'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)