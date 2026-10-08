import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, on="SN")

result = joined[["SN", "Price_x"]].copy()
result.columns = ["SN", "Price"]
result["SN"] = result["SN"].astype(str)
result["Price"] = result["Price"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)