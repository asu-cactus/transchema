import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="track_id", how="left")

result = merged[["index_track", "track_id"]].copy()
result["dummy"] = 1

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)