import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
result = df0.groupby('condition', as_index=False).agg({'click':'count'})
result = result.rename(columns={'click':'0'})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)