import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="city", how="inner")

df = df[["city", "driver_count", "fare", "ride_id"]]

df["driver_count"] = df["driver_count"].astype("Int64")
df["fare"] = df["fare"].astype(float)
df["ride_id"] = df["ride_id"].astype(float)
df["city"] = df["city"].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)