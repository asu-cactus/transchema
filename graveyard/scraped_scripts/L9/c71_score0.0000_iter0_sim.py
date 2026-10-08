import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_9.csv", index_col=0)

j01 = pd.merge(s0, s1, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('_x', '_y'))
j012 = pd.merge(j01, s2, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_2'))
j0123 = pd.merge(j012, s3, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_3'))
j01234 = pd.merge(j0123, s4, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_4'))
j012345 = pd.merge(j01234, s5, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_5'))
j0123456 = pd.merge(j012345, s6, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_6'))
j01234567 = pd.merge(j0123456, s7, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_7'))
j012345678 = pd.merge(j01234567, s8, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_8'))
final = pd.merge(j012345678, s9, how='inner', left_on=['bid_id', 'message_timestamp'], right_on=['sampled_bid_id', 'message_timestamp'], suffixes=('', '_9'))

final = final.rename(columns={'sampled_bid_id': 'bid_id'})

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_71/target_multisource_mcts.csv", index=False)