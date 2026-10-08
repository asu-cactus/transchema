import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_1.csv", index_col=0)

grouped_source0 = source0.groupby("city", as_index=False)["fare"].mean()

result = pd.merge(grouped_source0, source1[["city", "type"]], on="city", how="inner")

result = result[["city", "type", "fare"]]
result["fare"] = result["fare"].astype(float)
result["city"] = result["city"].astype(str)
result["type"] = result["type"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_70/target_multisource_mcts.csv", index=False)