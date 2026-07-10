import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="track_id", how="inner")

result = merged.groupby("index_track", as_index=False).agg({
    "track_id": "max",
    "dummy": "max"
})

result["index_track"] = result["index_track"].astype(int)
result["track_id"] = result["track_id"].astype(int)
result["dummy"] = result["dummy"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)