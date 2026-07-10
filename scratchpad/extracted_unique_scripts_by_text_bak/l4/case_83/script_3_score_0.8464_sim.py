import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby("city", as_index=False).agg(average_fare=("fare", "mean"))

merged = pd.merge(df1, grouped, how="inner", on="city")

merged["driver_count"] = merged["driver_count"].astype("Int64")
merged["type"] = merged["type"].astype(str)
merged["city"] = merged["city"].astype(str)
merged["average_fare"] = merged["average_fare"].astype(float)

result = merged[["city", "driver_count", "type", "average_fare"]]

result.to_csv(target_path, index=False)