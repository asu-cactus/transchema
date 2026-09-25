import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# Join source1 and source0 on track_id
merged = pd.merge(source1, source0, how="inner", on="track_id")

# Select columns as per target schema
result = merged[["index_track", "track_id", "dummy"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)