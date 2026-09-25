import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="shot_id_number", suffixes=('', '_dup'))

grouped = joined.groupby('area_of_shot').agg(
    is_goal=('is_goal', 'mean'),
    area_shot_sum=('distance_of_shot', 'sum'),
    is_goal_count=('is_goal', 'count')
).reset_index()

grouped['area_shot_sum'] = grouped['area_shot_sum'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)