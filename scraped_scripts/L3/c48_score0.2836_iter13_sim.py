import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

union_1_2 = pd.concat([s1, s2], ignore_index=True, sort=False)

joined_1 = pd.merge(union_1_2, s3, on="track_id", how="inner")

joined_2 = pd.merge(joined_1, s0, on="track_id", how="inner")

result = joined_2[["track_id", "dummy", "playlist_id", "interaction", "index_playlist", "index_track"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)