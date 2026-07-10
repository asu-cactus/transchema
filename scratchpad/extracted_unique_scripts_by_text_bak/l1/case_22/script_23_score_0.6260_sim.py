import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)