import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_2.csv", index_col=0)

join_1 = pd.merge(source2, source1, on="track_id", how="inner")
join_2 = pd.merge(join_1, source0, on="playlist_id", how="inner")

grouped = join_2.groupby(
    ["playlist_id", "track_id", "interaction", "index_playlist", "index_track"],
    as_index=False
).size().rename(columns={"size": "count"})

# The target schema does not require aggregation count, so just drop duplicates by grouping keys
result = grouped.drop(columns=["count"])

result = result.astype({
    "playlist_id": "int64",
    "track_id": "int64",
    "interaction": "int64",
    "index_playlist": "int64",
    "index_track": "int64"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_88/target_multisource_mcts.csv", index=False)