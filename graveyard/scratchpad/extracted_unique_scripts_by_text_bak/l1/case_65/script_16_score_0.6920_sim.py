import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
result = df.groupby("year", as_index=False).size().rename(columns={"size": "0"})
result["0"] = result["0"].astype(int)
result["year"] = result["year"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)