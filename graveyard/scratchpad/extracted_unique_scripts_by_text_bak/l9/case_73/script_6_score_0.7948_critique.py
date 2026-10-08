import pandas as pd

# Read all sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv", index_col=0)

# Rename src5 columns to align with others
src5_renamed = src5.rename(columns={'sampled_bid_id': 'bid_id', 'message': 'pii_cleaned_message'})

# Select only needed columns from all sources: bid_id and message column (pii_cleaned_message)
# For src5_renamed, columns are bid_id and pii_cleaned_message
# For others, columns are bid_id and pii_cleaned_message

dfs = [
    src0[['bid_id', 'pii_cleaned_message']],
    src1[['bid_id', 'pii_cleaned_message']],
    src2[['bid_id', 'pii_cleaned_message']],
    src3[['bid_id', 'pii_cleaned_message']],
    src4[['bid_id', 'pii_cleaned_message']],
    src5_renamed[['bid_id', 'pii_cleaned_message']],
    src6[['bid_id', 'pii_cleaned_message']],
    src7[['bid_id', 'pii_cleaned_message']],
    src8[['bid_id', 'pii_cleaned_message']],
    src9[['bid_id', 'pii_cleaned_message']],
]

# Concatenate all
union_df = pd.concat(dfs, ignore_index=True)

# Rename 'pii_cleaned_message' to 'message' to match target schema
union_df = union_df.rename(columns={'pii_cleaned_message': 'message'})

# Convert bid_id to int (target schema)
union_df['bid_id'] = union_df['bid_id'].astype(int)

# Group by bid_id and take the first message per bid_id (to ensure unique bid_id rows)
result = union_df.groupby('bid_id', as_index=False).agg({'message': 'first'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)