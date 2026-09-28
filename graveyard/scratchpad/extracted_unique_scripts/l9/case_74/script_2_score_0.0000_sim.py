import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_9.csv", index_col=0)

df = pd.merge(src0, src1, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['sampled_bid_id', 'message_timestamp'],
              suffixes=('_x', '_y'))

df = pd.merge(df, src2, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_2'))

df = pd.merge(df, src3, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_3'))

df = pd.merge(df, src4, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_4'))

df = pd.merge(df, src5, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_5'))

df = pd.merge(df, src6, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_6'))

df = pd.merge(df, src7, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_7'))

df = pd.merge(df, src8, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_8'))

df = pd.merge(df, src9, how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['bid_id', 'message_timestamp'],
              suffixes=('', '_9'))

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_74/target_multisource_mcts.csv", index=False)