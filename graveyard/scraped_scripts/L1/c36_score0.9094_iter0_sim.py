import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_36/target_multisource_mcts.csv", index=False)