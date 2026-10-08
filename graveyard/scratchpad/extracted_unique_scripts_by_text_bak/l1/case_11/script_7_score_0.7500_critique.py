import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv")

result = df0.groupby("sex", as_index=False)["births"].sum()

result["sex"] = result["sex"].astype(str)
result["births"] = result["births"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)