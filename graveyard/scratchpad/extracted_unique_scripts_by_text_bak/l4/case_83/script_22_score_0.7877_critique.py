import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on='city', how='inner')

result = merged.groupby(['city', 'driver_count', 'type'], as_index=False).agg(average_fare=('fare', 'mean'))

result['driver_count'] = result['driver_count'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)