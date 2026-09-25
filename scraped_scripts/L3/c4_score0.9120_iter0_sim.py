import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_0.csv", index_col=0)
result = df0.groupby("SN", as_index=False)["Price"].mean()
result["SN"] = result["SN"].astype(str)
result["Price"] = result["Price"].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_4/target_multisource_mcts.csv", index=False)