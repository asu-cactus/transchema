import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

result = pd.concat([df0, df1], ignore_index=True)
result = result.astype({'0': float, '1': float, '2': float, '3': float})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)