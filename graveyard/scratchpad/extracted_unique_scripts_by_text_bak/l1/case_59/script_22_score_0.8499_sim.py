import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

result = df0.groupby("PRODUCTLINE", dropna=False)["SALES"].sum().reset_index()

result["PRODUCTLINE"] = result["PRODUCTLINE"].astype(str)
result["SALES"] = result["SALES"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)