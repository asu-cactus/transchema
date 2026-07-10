import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

# Add 'outcome' column to source1 with NaN to match source2 schema for union
source1['outcome'] = pd.NA

# Union source1 and source2
unioned = pd.concat([source1, source2], ignore_index=True, sort=False)

# Join source0 with unioned on 'bidder_id'
joined = pd.merge(source0, unioned, on='bidder_id', how='inner')

# Group by bidder_id, payment_account, address, outcome, country and count bids
result = joined.groupby(
    ['bidder_id', 'payment_account', 'address', 'outcome', 'country'], as_index=False
).agg(bids_count=('bid_id', 'count'))

# Ensure columns order matches target schema
result = result[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)