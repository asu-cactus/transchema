import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

grouped = source1.groupby('city', as_index=False)['fare'].mean()

merged = pd.merge(source0, grouped, on='city', how='inner')

result = merged.groupby(['type', 'city'], as_index=False)['fare'].mean()

result = result.rename(columns={'fare': 'fare', 'city': 'city', 'type': 'type'})

result = result[['city', 'type', 'fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)