import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_3.csv", index_col=0)

union_result = pd.concat([source0, source3], ignore_index=True)

join_result_1 = pd.merge(union_result, source2, on="playlist_id", how="inner")

final_join = pd.merge(join_result_1, source1, on="track_id", how="inner")

target = final_join[["playlist_id", "track_id", "interaction", "index_playlist", "index_track"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_88/target_multisource_mcts.csv", index=False)