import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

agg = s2.groupby("track_id").agg(
    min_playlist_id=pd.NamedAgg(column="playlist_id", aggfunc="min"),
    max_playlist_id=pd.NamedAgg(column="playlist_id", aggfunc="max"),
    avg_interaction=pd.NamedAgg(column="interaction", aggfunc="mean"),
).reset_index()

agg["interaction"] = agg["avg_interaction"].round().astype("Int64")
agg = agg.drop(columns=["avg_interaction"])

joined_0 = pd.merge(agg, s0, on="track_id", how="inner")

joined_1 = pd.merge(joined_0, s1, left_on="min_playlist_id", right_on="playlist_id", how="inner")

final = pd.merge(joined_1, s3, on="track_id", how="inner")

final["playlist_id"] = final["max_playlist_id"]
final["dummy"] = final["dummy"].astype("Int64")
final["playlist_id"] = final["playlist_id"].astype("Int64")
final["index_playlist"] = final["index_playlist"].astype("Int64")
final["index_track"] = final["index_track"].astype("Int64")
final["track_id"] = final["track_id"].astype("Int64")
final["interaction"] = final["interaction"].astype("Int64")

result = final[["track_id", "dummy", "playlist_id", "interaction", "index_playlist", "index_track"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)