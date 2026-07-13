import pandas as pd

src0_path = 'autopipeline-benchmarks/github-pipelines/length4_21/test_0.csv'
df0 = pd.read_csv(src0_path, index_col=0)

grouped = df0.groupby('game_season').agg(
    season_sum=('game_season', 'size'),
    is_goal_count1=('is_goal', lambda x: (x == 1).sum())
).reset_index()

grouped['is_goal'] = 0.0

grouped = grouped[['game_season', 'is_goal', 'season_sum', 'is_goal_count1']]

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts_recovery_test_val.csv', index=False)