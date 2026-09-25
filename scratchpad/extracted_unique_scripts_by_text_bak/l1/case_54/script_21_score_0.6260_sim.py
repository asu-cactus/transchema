import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv", index_col=0)
result = pd.concat([df0], ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)