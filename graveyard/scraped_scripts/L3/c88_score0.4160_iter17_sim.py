import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_3.csv", index_col=0)

join_2_1 = pd.merge(source2, source1, on="track_id", how="inner")

source3['track_id'] = pd.NA
source3['interaction'] = pd.NA
union_result = pd.concat([join_2_1, source3], ignore_index=True, sort=False)

final = pd.merge(union_result, source0, on="playlist_id", how="inner")

final = final[['playlist_id', 'track_id', 'interaction', 'index_playlist', 'index_track']]

final['playlist_id'] = final['playlist_id'].astype('Int64')
final['track_id'] = final['track_id'].astype('Int64')
final['interaction'] = final['interaction'].astype('Int64')
final['index_playlist'] = final['index_playlist'].astype('Int64')
final['index_track'] = final['index_track'].astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_88/target_multisource_mcts.csv", index=False)