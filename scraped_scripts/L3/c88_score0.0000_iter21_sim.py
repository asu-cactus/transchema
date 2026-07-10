import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_88/training_3.csv", index_col=0)

union_result = pd.concat([src0, src3], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, src2, on="playlist_id", how="inner")

final_join = pd.merge(join_result_1, src1, on="track_id", how="inner")

final = final_join[['playlist_id', 'track_id', 'interaction', 'index_playlist', 'index_track']]

final = final.astype({
    'playlist_id': 'int64',
    'track_id': 'int64',
    'interaction': 'int64',
    'index_playlist': 'int64',
    'index_track': 'int64'
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_88/target_multisource_mcts.csv", index=False)