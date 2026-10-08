import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

groupby_result = df1.groupby("city", as_index=False).agg({
    "fare": "mean",
    "ride_id": "mean"
})

joined = pd.merge(df0, groupby_result, on="city", how="inner")

result = joined[["city", "driver_count", "fare", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)