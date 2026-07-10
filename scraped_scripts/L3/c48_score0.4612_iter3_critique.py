import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

result = pd.merge(source2, source0, on="track_id", how="left")
result = pd.merge(result, source1, on="playlist_id", how="left")
result = pd.merge(result, source3, on="track_id", how="left")

result = result[['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)