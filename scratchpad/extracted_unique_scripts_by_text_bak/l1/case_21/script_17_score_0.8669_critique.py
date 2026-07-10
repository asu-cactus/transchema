import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)

# Group by Major_category and compute mean of Median
result = df0.groupby('Major_category', as_index=False)['Median'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)