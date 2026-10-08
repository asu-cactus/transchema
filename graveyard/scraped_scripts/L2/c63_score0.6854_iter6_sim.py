import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_df1 = df1.groupby("city").agg(
    fare=("fare", "sum"),
    ride_id=("ride_id", pd.Series.nunique)
).reset_index()

merged = pd.merge(df0, agg_df1, how="inner", on="city")

merged = merged.rename(columns={"ride_id": "ride_id", "driver_count": "driver_count", "fare": "fare", "city": "city"})

merged = merged[["city", "driver_count", "fare", "ride_id"]]

merged["driver_count"] = merged["driver_count"].astype("Int64")
merged["fare"] = merged["fare"].astype(float)
merged["ride_id"] = merged["ride_id"].astype(float)
merged["city"] = merged["city"].astype(str)

merged.to_csv(target_path, index=False)