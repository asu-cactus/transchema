import pandas as pd

# Read sources with index_col=0 as instructed
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

# Join s0 and s2 on track_id
join_0_2 = pd.merge(s0, s2, on='track_id', how='inner')

# Join the above with s1 on playlist_id
join_0_2_1 = pd.merge(join_0_2, s1, on='playlist_id', how='inner')

# Join the above with s3 on track_id
final_join = pd.merge(join_0_2_1, s3, on='track_id', how='inner')

# Group by track_id to ensure uniqueness, aggregate other columns by max (safe if consistent)
final = final_join.groupby('track_id', dropna=False).agg({
    'dummy': 'max',
    'playlist_id': 'max',
    'interaction': 'max',
    'index_playlist': 'max',
    'index_track': 'max'
}).reset_index()

# Reorder columns to match target schema exactly
final = final[['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)