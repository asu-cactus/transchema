import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

joined = pd.merge(source1, source0, on='city', how='inner')

grouped = joined.groupby('city', as_index=False).agg(
    driver_count=('driver_count', 'first'),
    type=('type', 'first'),
    average_fare=('fare', 'mean')
)

grouped['driver_count'] = grouped['driver_count'].astype(int)
grouped['city'] = grouped['city'].astype(str)
grouped['type'] = grouped['type'].astype(str)
grouped['average_fare'] = grouped['average_fare'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)