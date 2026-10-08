import pandas as pd

# Read sources with index_col=0 as instructed
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_48/training_3.csv", index_col=0)

# Join s0 and s2 on track_id
join_0_2 = pd.merge(s0, s2, on='track_id', how='inner')

# Join with s1 on playlist_id
join_0_2_1 = pd.merge(join_0_2, s1, on='playlist_id', how='inner')

# Join with s3 on track_id
join_all = pd.merge(join_0_2_1, s3, on='track_id', how='inner')

# Group by track_id and aggregate by taking first value of other columns
# This assumes no duplicates per track_id after join, or that first is representative
final_df = join_all.groupby('track_id', as_index=False).agg({
    'dummy': 'first',
    'playlist_id': 'first',
    'interaction': 'first',
    'index_playlist': 'first',
    'index_track': 'first'
})

# Reorder columns to match target schema exactly
final_df = final_df[['track_id', 'dummy', 'playlist_id', 'interaction', 'index_playlist', 'index_track']]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_48/target_multisource_mcts.csv", index=False)