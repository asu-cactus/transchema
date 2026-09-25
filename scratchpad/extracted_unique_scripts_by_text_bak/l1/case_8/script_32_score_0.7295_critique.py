import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)  # columns: track_id, dummy
df1 = pd.read_csv(source1_path, index_col=0)  # columns: index_track, track_id

# Join on track_id
joined = pd.merge(df1, df0, how='inner', on='track_id')

# Ensure column order and types as target schema
joined = joined[['index_track', 'track_id', 'dummy']]

joined['index_track'] = joined['index_track'].astype('Int64')
joined['track_id'] = joined['track_id'].astype('Int64')
joined['dummy'] = joined['dummy'].astype('Int64')

joined.to_csv(target_path, index=False)