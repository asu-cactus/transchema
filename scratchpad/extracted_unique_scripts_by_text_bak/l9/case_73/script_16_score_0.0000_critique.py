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

# List of sources with same schema (except src5)
same_schema_sources = [src0, src1, src2, src3, src4, src6, src7, src8, src9]

# For these sources, rename 'pii_cleaned_message' to 'message' to align with target schema
for i, df in enumerate(same_schema_sources):
    same_schema_sources[i] = df.rename(columns={'pii_cleaned_message': 'message'})[['bid_id', 'message']]

# Union all these sources
union_others = pd.concat(same_schema_sources, ignore_index=True, sort=False)

# For src5, rename 'sampled_bid_id' to 'bid_id' to align keys
src5_renamed = src5.rename(columns={'sampled_bid_id': 'bid_id'})[['bid_id', 'message']]

# Union src5 with the union of other sources
final_union = pd.concat([union_others, src5_renamed], ignore_index=True, sort=False)

# Group by bid_id and message to remove duplicates (target examples have unique bid_id-message pairs)
result = final_union.dropna(subset=['bid_id', 'message']).copy()
result = result.astype({'bid_id': 'Int64', 'message': 'string'})
result = result.drop_duplicates(subset=['bid_id', 'message'])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)