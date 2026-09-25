import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_1.csv", index_col=0)

grouped = df0.groupby("city", as_index=False).agg({"fare":"mean", "ride_id":"count"})
grouped = grouped.rename(columns={"fare":"fare", "ride_id":"ride_id", "city":"city"})

merged = pd.merge(grouped, df1, how="inner", on="city")

result = merged[["type", "fare", "ride_id", "driver_count"]].copy()
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)
result["driver_count"] = result["driver_count"].astype(int)
result["type"] = result["type"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_72/target_multisource_mcts.csv", index=False)