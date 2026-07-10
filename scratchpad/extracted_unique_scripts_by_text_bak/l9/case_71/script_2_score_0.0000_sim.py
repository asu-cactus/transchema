import pandas as pd

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

join01 = pd.merge(src0, src1, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('_x', '_y'))
join012 = pd.merge(join01, src2, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_2'))
join0123 = pd.merge(join012, src3, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_3'))
join01234 = pd.merge(join0123, src4, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_4'))
join012345 = pd.merge(join01234, src5, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_5'))
join0123456 = pd.merge(join012345, src6, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_6'))
join01234567 = pd.merge(join0123456, src7, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_7'))
join012345678 = pd.merge(join01234567, src8, how='inner', on=['bid_id', 'message_timestamp'], suffixes=('', '_8'))

# For src9, join on src9.sampled_bid_id = bid_id and message_timestamp
join_final = pd.merge(join012345678, src9, how='inner', left_on=['bid_id', 'message_timestamp'], right_on=['sampled_bid_id', 'message_timestamp'], suffixes=('', '_9'))

# Rename columns to match target schema exactly
# The target schema has many columns with suffixes _x, _y, _x_x, _y_x, etc.
# The source columns from src0 have suffix _x, from src1 have suffix _y, from src9 have no suffix or _9.
# The other sources (src2 to src8) have no suffix or _2, _3, etc. We keep their columns as is.

# Drop duplicated columns from merges (like bid_id_header from multiple sources)
# Keep bid_id and message_timestamp as is
# Rename src9.sampled_bid_id to bid_id (already have bid_id from src0 etc.)

# Drop sampled_bid_id column from join_final as bid_id is already present
join_final.drop(columns=['sampled_bid_id'], inplace=True)

# Convert bid_id to int (if not already)
join_final['bid_id'] = join_final['bid_id'].astype(int)

# Convert message_timestamp to string (if not already)
join_final['message_timestamp'] = join_final['message_timestamp'].astype(str)

# Save to target CSV
join_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_71/target_multisource_mcts.csv", index=False)