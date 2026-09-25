import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)
result = pd.concat([df0], ignore_index=True)
result = result.astype({"user_id": str, "email": str, "geo": str})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)