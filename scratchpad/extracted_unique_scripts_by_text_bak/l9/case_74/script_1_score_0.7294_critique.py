import pandas as pd

# Read all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_7.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_74/training_9.csv", index_col=0)

# Union all tables with the same schema (except src1 and src8)
union_tables = [src0, src2, src3, src4, src5, src6, src7, src9]
unioned = pd.concat(union_tables, ignore_index=True, sort=False)

# Join unioned table with src1 on bid_id = sampled_bid_id and message_timestamp
df = pd.merge(unioned, src1,
              how='inner',
              left_on=['bid_id', 'message_timestamp'],
              right_on=['sampled_bid_id', 'message_timestamp'],
              suffixes=('', '_src1'))

# Drop the redundant 'sampled_bid_id' column after join to match target schema
df.drop(columns=['sampled_bid_id'], inplace=True)

# Write output with exact column names as in target schema
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_74/target_multisource_mcts.csv", index=False)