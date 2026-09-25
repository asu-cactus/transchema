import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df1, df0, on="city", how="inner")

agg = merged.groupby("city").agg({
    "fare": "min",
    "ride_id": "max",
    "driver_count": "max"
}).reset_index()

agg = agg.rename(columns={
    "fare": "fare",
    "ride_id": "ride_id",
    "driver_count": "driver_count",
    "city": "city"
})

agg["driver_count"] = agg["driver_count"].astype("Int64")
agg["fare"] = agg["fare"].astype(float)
agg["ride_id"] = agg["ride_id"].astype(float)
agg["city"] = agg["city"].astype(str)

agg.to_csv(target_path, index=False)