import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_72/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_72/training_1.csv", index_col=0)

grouped_0 = source0.groupby("city", as_index=False).agg({"fare": "sum"})

merged = pd.merge(grouped_0, source1[["city", "type"]], on="city", how="inner")

merged = merged[["city", "type", "fare"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_72/target_multisource_mcts.csv", index=False)