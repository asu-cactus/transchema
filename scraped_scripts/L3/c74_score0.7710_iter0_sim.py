import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_74/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_74/training_1.csv", index_col=0)

grouped_source0 = source0.groupby("city", as_index=False)["fare"].mean()

merged = pd.merge(grouped_source0, source1[["city", "type"]], on="city")

merged["fare"] = merged["fare"].astype(float)
merged["city"] = merged["city"].astype(str)
merged["type"] = merged["type"].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_74/target_multisource_mcts.csv", index=False)