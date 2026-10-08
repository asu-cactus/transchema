import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="shot_id_number", suffixes=('', '_dup'))

agg = joined.groupby(['type_of_combined_shot', 'is_goal'], dropna=False).agg(
    shot_sum=('shot_id_number', 'sum'),
    is_goal_count1=('is_goal', 'count')
).reset_index()

agg['is_goal'] = agg['is_goal'].astype(float)
agg['type_of_combined_shot'] = agg['type_of_combined_shot'].astype(str)

agg = agg[['type_of_combined_shot', 'is_goal', 'shot_sum', 'is_goal_count1']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)