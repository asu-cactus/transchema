import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

joined = pd.merge(source1, source0, how="inner", on="city")

result = joined[["city", "driver_count"]].rename(columns={"driver_count": "type"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)