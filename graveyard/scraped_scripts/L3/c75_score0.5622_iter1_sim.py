import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_75/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="city", how="inner")

result = merged[["city", "type", "fare"]].copy()
result["city"] = result["city"].astype(str)
result["type"] = result["type"].astype(str)
result["fare"] = result["fare"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_75/target_multisource_mcts.csv", index=False)