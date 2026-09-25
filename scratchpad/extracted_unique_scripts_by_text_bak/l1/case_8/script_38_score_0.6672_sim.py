import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

grouped = source1.groupby("index_track", as_index=False).agg({"track_id": "min"})

merged = pd.merge(grouped, source0, how="left", left_on="track_id", right_on="track_id")

result = merged[["index_track", "track_id", "dummy"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)