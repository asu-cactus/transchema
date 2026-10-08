import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join on city
join_result = pd.merge(source1, source0, on="city", how="inner")

# Group by city and compute average fare
agg = join_result.groupby("city", as_index=False).agg(average_fare=("fare", "mean"))

# Merge back driver_count and type from source1 (unique per city)
final = pd.merge(agg, source1, on="city", how="left")

# Reorder columns to match target schema
final = final[["city", "driver_count", "type", "average_fare"]]

# Ensure correct types
final["driver_count"] = final["driver_count"].astype(int)
final["city"] = final["city"].astype(str)
final["type"] = final["type"].astype(str)
final["average_fare"] = final["average_fare"].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)