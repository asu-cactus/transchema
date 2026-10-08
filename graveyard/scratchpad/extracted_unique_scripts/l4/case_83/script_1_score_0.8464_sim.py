import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

grouped = df0.groupby("city", as_index=False).agg(average_fare=("fare", "mean"))

merged = pd.merge(df1, grouped, on="city", how="inner")

result = merged[["city", "driver_count", "type", "average_fare"]]

result["driver_count"] = result["driver_count"].astype(int)
result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)
result["average_fare"] = result["average_fare"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)