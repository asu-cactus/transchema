import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
result = df0.groupby("Gender", as_index=False).size().rename(columns={"size": "0"})
result["0"] = result["0"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)