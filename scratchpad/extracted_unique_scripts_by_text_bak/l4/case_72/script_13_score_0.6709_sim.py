import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

agg1 = df1.groupby("city").agg(a=("driver_count", "mean"), b=("type", "count")).reset_index()

joined = pd.merge(df0, agg1, on="city", how="inner")

agg2 = joined.groupby("city").agg(a_fare=("fare", "mean"), b_ride=("ride_id", "count")).reset_index()

final = pd.merge(agg1, agg2, on="city", how="inner")

final["a"] = final["a"]
final["b"] = final["b"]

final = final[["city", "a", "b"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)