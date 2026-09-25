import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

grouped_source0 = df0.groupby("city").agg(driver_count=("ride_id", "nunique")).reset_index()

joined = pd.merge(grouped_source0, df1[["city", "driver_count"]], on="city", how="outer", suffixes=("", "_1"))

joined["driver_count"] = joined["driver_count"].fillna(0) + joined["driver_count_1"].fillna(0)
result = joined[["city", "driver_count"]]
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)