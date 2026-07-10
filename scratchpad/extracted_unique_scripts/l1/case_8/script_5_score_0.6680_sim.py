import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby('track_id').agg(
    index_track_count=('index_track', 'count'),
    index_track_min=('index_track', 'min'),
    index_track_max=('index_track', 'max')
).reset_index()

joined = pd.merge(df0, agg, how='left', on='track_id')

joined['index_track'] = joined['index_track_min'].combine_first(joined['index_track_max']).combine_first(joined['index_track_count'])
joined = joined[['index_track', 'track_id', 'dummy']]

joined['index_track'] = joined['index_track'].astype('Int64')
joined['track_id'] = joined['track_id'].astype('Int64')
joined['dummy'] = joined['dummy'].astype('Int64')

joined.to_csv(target_path, index=False)