import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="Item ID")

grouped = joined.groupby("SN_x").agg(Price=("Price_x", "mean"), count=("Item ID", "count")).reset_index()

grouped = grouped.rename(columns={"SN_x": "SN", "Price": "Price", "count": "count"})

grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped["count"] = grouped["count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)