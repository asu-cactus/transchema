import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

agg = df1.groupby("city").agg(fare=("fare", "mean"), ride_id=("ride_id", "count")).reset_index()

merged = pd.merge(df0, agg, on="city", how="inner")

merged = merged.rename(columns={"ride_id": "ride_id", "fare": "fare", "driver_count": "driver_count", "type": "type", "city": "city"})

merged["ride_id"] = merged["ride_id"].astype(int)
merged["driver_count"] = merged["driver_count"].astype(int)
merged["fare"] = merged["fare"].astype(float)
merged["date"] = ""  # date column missing in sources, fill with empty string

merged = merged[["city", "driver_count", "type", "date", "fare", "ride_id"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)