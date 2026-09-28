import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_72/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_72/test_1.csv', index_col=0)

grouped0 = df0.groupby('city').agg(
    a=('fare', 'mean'),
    ride_count=('ride_id', 'count')
).reset_index()

merged = pd.merge(grouped0, df1, on='city')

merged['b'] = merged['ride_count'] + merged['driver_count']

merged[['city', 'a', 'b']].to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts_recovery_test_val.csv',
    index=False
)