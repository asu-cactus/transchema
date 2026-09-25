import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

join_result = pd.merge(source1, source0, on="city", how="inner")

agg = join_result.groupby(["city", "driver_count", "type"], as_index=False).agg(average_fare=("fare", "mean"))

agg["driver_count"] = agg["driver_count"].astype(int)
agg["city"] = agg["city"].astype(str)
agg["type"] = agg["type"].astype(str)
agg["average_fare"] = agg["average_fare"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)