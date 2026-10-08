import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)
result = df0.groupby('condition', as_index=False).agg({'click': 'mean'})
result = result.astype({'condition': 'int64', 'click': 'float64'})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)