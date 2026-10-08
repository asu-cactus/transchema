import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_1.csv", index_col=0)

joined = pd.merge(source0, source1, on="city", how="inner")

result = joined.groupby("city", as_index=False)["driver_count"].sum()
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_69/target_multisource_mcts.csv", index=False)