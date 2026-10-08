import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_3.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_2.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_0.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_1.csv", index_col=0)

groupby_result = s0.groupby("playlist_id", as_index=False).size().rename(columns={"size": "count"})

join_result_1 = pd.merge(groupby_result, s1, on="playlist_id", how="inner")
join_result_2 = pd.merge(join_result_1, s2, on="playlist_id", how="inner")
final_join = pd.merge(join_result_2, s3, on="track_id", how="inner")

result = final_join[["playlist_id", "track_id", "interaction", "index_playlist", "index_track"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_88/target_multisource_mcts.csv", index=False)