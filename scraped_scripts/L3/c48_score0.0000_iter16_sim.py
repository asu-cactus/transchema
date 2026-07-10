import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)

union_result = pd.concat([s0.rename(columns={'dummy':'dummy', 'track_id':'track_id'}),
                          s3.rename(columns={'index_track':'index_track', 'track_id':'track_id'})], 
                         sort=False, ignore_index=True)

# union_result has columns: track_id, dummy (from s0) and index_track, track_id (from s3)
# After concat, columns are union of all columns, missing values are NaN

# Join union_result with s1 on union_result.index_track == s1.index_playlist
# union_result has index_track only from s3 rows, s0 rows have NaN in index_track
join_result_1 = pd.merge(union_result, s1, left_on='index_track', right_on='index_playlist', how='inner')

# join_result_1 columns: track_id, dummy, index_track, index_playlist, playlist_id

# Join join_result_1 with s2 on playlist_id and track_id
final_join = pd.merge(join_result_1, s2, on=['playlist_id', 'track_id'], how='inner')

# final_join columns: track_id, dummy, index_track, index_playlist, playlist_id, interaction

# Reorder columns to target schema: ['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']
target = final_join[['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)