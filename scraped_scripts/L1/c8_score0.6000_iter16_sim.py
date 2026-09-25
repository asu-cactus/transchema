import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

df0_renamed = df0.copy()
df0_renamed['index_track'] = pd.NA
cols_order_0 = ['index_track', 'track_id', 'dummy']
df0_renamed = df0_renamed[cols_order_0]

union_result = df0_renamed

result = pd.merge(union_result, df1, on='track_id', how='outer', suffixes=('_left', '_right'))

result['index_track'] = result['index_track_right'].combine_first(result['index_track_left'])
result['dummy'] = result['dummy'].fillna(1).astype('Int64')

final = result[['index_track', 'track_id', 'dummy']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)