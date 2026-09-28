import pandas as pd

source_df = pd.read_csv(
    'autopipeline-benchmarks/github-pipelines/length4_18/test_0.csv',
    index_col=0
)

aggregated_df = source_df.groupby('area_of_shot', as_index=False).agg(
    area_shot_sum=('area_of_shot', 'count'),
    is_goal_count=('is_goal', 'sum')
)
aggregated_df['area_shot_sum'] = aggregated_df['area_shot_sum'].astype(int)
aggregated_df['is_goal_count'] = aggregated_df['is_goal_count'].astype(int)

result_df = pd.merge(
    source_df[['area_of_shot', 'is_goal']],
    aggregated_df,
    on='area_of_shot',
    how='left'
)

result_df.to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts_recovery_test_val.csv',
    index=False
)