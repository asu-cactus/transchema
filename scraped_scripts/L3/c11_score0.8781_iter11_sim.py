import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

joined = pd.merge(df0, df0, on="SN", suffixes=('_left', '_right'))

agg = joined.groupby("SN").agg(
    Price=("Price_left", "min"),
    count=("SN", "count")
).reset_index()

agg["Price"] = agg["Price"].astype(float)
agg["count"] = agg["count"].astype(int)
agg["SN"] = agg["SN"].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)