import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_61/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_61/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_61/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df.astype({'0': float, '1': float, '2': float, '3': float})

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_61/target_multisource_mcts.csv", index=False)