import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on='city', how='inner')

result = merged.groupby('city', as_index=False).agg({'type': 'first', 'fare': 'mean'})

result = result[['city', 'type', 'fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)