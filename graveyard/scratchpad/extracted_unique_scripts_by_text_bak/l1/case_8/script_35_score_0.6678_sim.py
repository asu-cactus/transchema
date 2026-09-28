import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

df0['index_track'] = pd.NA
union_result = df0[['index_track', 'track_id', 'dummy']]

df1['dummy'] = pd.NA
df1 = df1[['index_track', 'track_id', 'dummy']]

result = pd.merge(union_result, df1, on='track_id', how='outer', suffixes=('_0', '_1'))

result['index_track'] = result['index_track_1'].combine_first(result['index_track_0'])
result['dummy'] = result['dummy_0'].combine_first(result['dummy_1'])

final = result[['index_track', 'track_id', 'dummy']].copy()
final['index_track'] = final['index_track'].astype('Int64')
final['track_id'] = final['track_id'].astype('Int64')
final['dummy'] = final['dummy'].astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)