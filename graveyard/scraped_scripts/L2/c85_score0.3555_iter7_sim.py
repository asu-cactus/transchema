import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="Mouse ID")
result = merged[["Drug", "Timepoint", "Mouse ID"]].copy()
result["Timepoint"] = result["Timepoint"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv", index=False)