import pandas as pd

# Read all source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv", index_col=0)

# Union all sources with the same schema (except s5)
union_sources = pd.concat(
    [s0, s1, s2, s3, s4, s6, s7, s8, s9],
    ignore_index=True,
    sort=False
)

# Select relevant columns and rename pii_cleaned_message to message for union_sources
union_sources = union_sources[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})

# Prepare s5: rename sampled_bid_id to bid_id to join, and keep message column as is
s5_renamed = s5.rename(columns={'sampled_bid_id': 'bid_id'})

# Join s5 with union_sources on bid_id
join_result = pd.merge(s5_renamed[['bid_id', 'message']], union_sources, on='bid_id', how='inner')

# Union the messages from s5 and union_sources
final_union = pd.concat(
    [s5_renamed[['bid_id', 'message']], union_sources],
    ignore_index=True,
    sort=False
)

# Group by bid_id and take the first message (to get unique bid_id rows)
final_df = final_union.groupby('bid_id', as_index=False).agg({'message': 'first'})

# Ensure correct types
final_df['bid_id'] = final_df['bid_id'].astype(int)
final_df['message'] = final_df['message'].astype(str)

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)