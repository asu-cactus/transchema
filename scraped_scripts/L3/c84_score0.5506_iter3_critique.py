import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

# Add 'outcome' column to source1 to match source0 schema for union
source1['outcome'] = pd.NA

# Reorder columns to match source0 exactly
source1 = source1[source0.columns]

# Union source0 and source1
union_source = pd.concat([source0, source1], ignore_index=True)

# Join union_source with source2 on 'bidder_id'
join_all = pd.merge(union_source, source2, on='bidder_id', how='inner')

# Group by leftmost non-float unique columns in target schema
grouped = join_all.groupby(
    ['bidder_id', 'payment_account', 'address', 'outcome', 'country'],
    as_index=False
).agg(bids_count=('bid_id', 'count'))

# Ensure bids_count is integer
grouped['bids_count'] = grouped['bids_count'].astype(int)

# Write output with exact target schema column order
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)