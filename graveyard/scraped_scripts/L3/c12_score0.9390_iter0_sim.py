import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv", index_col=0)

grouped = df0.groupby("SN", as_index=False).agg(
    Price=("Price", "first"),
    count=("SN", "count")
)

grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped["count"] = grouped["count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)