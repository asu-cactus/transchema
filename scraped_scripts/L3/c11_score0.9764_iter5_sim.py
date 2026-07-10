import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

agg = df0.groupby("SN").agg(Price=("Price", "sum"), count=("Purchase ID", "count")).reset_index()

agg["SN"] = agg["SN"].astype(str)
agg["Price"] = agg["Price"].astype(float)
agg["count"] = agg["count"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)