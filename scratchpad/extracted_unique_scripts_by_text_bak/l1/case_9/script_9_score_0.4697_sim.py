import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)
result = df[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)