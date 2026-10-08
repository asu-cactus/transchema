import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="city", how="inner")

result = merged.groupby("city").agg(driver_count=("ride_id", "count")).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)