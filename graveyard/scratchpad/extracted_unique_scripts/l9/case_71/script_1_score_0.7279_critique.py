import pandas as pd

# Read all source files with index_col=0 to ignore the first index column
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_71/training_9.csv", index_col=0)

# UNION all src0 to src8 (all have the same schema)
union_0_8 = pd.concat([src0, src1, src2, src3, src4, src5, src6, src7, src8], ignore_index=True)

# Join unioned table with src9 on bid_id = sampled_bid_id and message_timestamp
joined = pd.merge(
    union_0_8,
    src9,
    how='inner',
    left_on=['bid_id', 'message_timestamp'],
    right_on=['sampled_bid_id', 'message_timestamp'],
    suffixes=('', '_9')
)

# Drop sampled_bid_id as bid_id already exists
joined.drop(columns=['sampled_bid_id'], inplace=True)

# Convert bid_id to int (if not already)
joined['bid_id'] = joined['bid_id'].astype(int)

# Convert message_timestamp to string (if not already)
joined['message_timestamp'] = joined['message_timestamp'].astype(str)

# The target schema expects columns without suffixes.
# The unioned tables have no suffixes, src9 columns have suffix _9.
# Rename src9 columns to match target schema (remove _9 suffix)
rename_map = {col: col[:-2] for col in joined.columns if col.endswith('_9')}
joined.rename(columns=rename_map, inplace=True)

# Save to target CSV
joined.to_csv("autopipeline-benchmarks/github-pipelines/length9_71/target_multisource_mcts.csv", index=False)