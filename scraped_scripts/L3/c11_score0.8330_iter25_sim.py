import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

grouped = df_union.groupby("SN", as_index=False).agg(
    Price=("Price", "mean"),
    count=("SN", "size")
)

grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped["count"] = grouped["count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)