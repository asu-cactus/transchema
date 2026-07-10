import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv", index_col=0)

groupby_result = source0.groupby('city', as_index=False).agg(driver_count=('ride_id', 'count'))

joined = pd.merge(source1, groupby_result, on='city', how='inner')

result = joined[['city', 'driver_count_x']].rename(columns={'driver_count_x': 'driver_count'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)