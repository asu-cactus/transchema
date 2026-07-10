import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

joined = pd.merge(df0, df0, on="SN")

grouped = joined.groupby("SN").agg(
    Price=("Price_x", "first"),
    count=("SN", "count")
).reset_index()

grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped["count"] = grouped["count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)