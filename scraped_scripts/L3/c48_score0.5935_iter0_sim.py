import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

groupby_result = s0.groupby('track_id', as_index=False).agg({'dummy':'max'})

join_result_1 = pd.merge(groupby_result, s2, on='track_id', how='inner')
join_result_2 = pd.merge(join_result_1, s0, on='track_id', how='inner')
join_result_3 = pd.merge(join_result_2, s3, on='track_id', how='inner')
final_join = pd.merge(join_result_3, s1, on='playlist_id', how='inner')

final = final_join[['track_id', 'dummy_x', 'playlist_id', 'interaction', 'index_playlist', 'index_track']]
final.columns = ['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)