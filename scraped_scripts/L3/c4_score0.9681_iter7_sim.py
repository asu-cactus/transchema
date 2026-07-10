import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_0.csv", index_col=0)

agg = df0.groupby("SN").agg({"Price": "sum", "Purchase ID": "count"}).reset_index()

agg["Price"] = agg["Price"].astype(float)
agg["SN"] = agg["SN"].astype(str)

target = agg[["SN", "Price"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_4/target_multisource_mcts.csv", index=False)