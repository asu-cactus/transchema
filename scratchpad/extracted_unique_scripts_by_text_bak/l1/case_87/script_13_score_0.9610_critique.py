import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

# Group by 'condition' and compute mean of 'click'
result = df.groupby('condition', as_index=False)['click'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)