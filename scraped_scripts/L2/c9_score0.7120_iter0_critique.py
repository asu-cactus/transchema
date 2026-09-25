import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv", index_col=0)

joined = pd.merge(source1, source0, on='city', how='inner')

result = joined.groupby('city', as_index=False).agg(driver_count=('driver_count', 'max'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)