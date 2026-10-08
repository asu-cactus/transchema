import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="Mouse ID")

result = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size()

result = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).first()

result = result[["Drug", "Timepoint", "Mouse ID"]]

result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].astype(int, errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)