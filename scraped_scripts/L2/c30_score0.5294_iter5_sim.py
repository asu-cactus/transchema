import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="city")
result = merged[["city", "fare"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_30/target_multisource_mcts.csv", index=False)