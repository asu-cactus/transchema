import pandas as pd

# Read sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

# src1 does not have 'outcome' column, add it with NaN to align schemas for union
src1['outcome'] = pd.NA

# UNION src0 and src1 on ['bidder_id', 'payment_account', 'address', 'outcome']
union_src = pd.concat([src0, src1], ignore_index=True)

# GROUP_BY src2 on ['bidder_id', 'country'], aggregate COUNT_DISTINCT on 'auction' as bids_count
agg_src2 = src2.groupby(['bidder_id', 'country'], as_index=False).agg(
    bids_count=('auction', 'nunique')
)

# JOIN unioned bidder info with aggregated bids info on 'bidder_id' (inner join)
# This will replicate bidder info for each country
result = pd.merge(union_src, agg_src2, how='inner', on='bidder_id')

# Select columns as per target schema
result = result[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)