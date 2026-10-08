import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

result = df0.groupby("sex", as_index=False).agg({"births": "sum"})

result["births"] = result["births"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)