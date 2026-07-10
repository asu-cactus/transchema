import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
result = df.groupby("condition", as_index=False).size().rename(columns={"size": "0"})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)