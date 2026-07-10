import pandas as pd

# Read sources
Source3_35_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
Source3_35_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
Source3_35_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

# Add 'outcome' column to Source3_35_1 with NaN (float) to match Source3_35_2 schema
Source3_35_1 = Source3_35_1.assign(outcome=pd.NA)

# UNION Source3_35_1 and Source3_35_2
union_df = pd.concat([Source3_35_1, Source3_35_2], ignore_index=True, sort=False)

# Join unioned table with Source3_35_0 on 'bidder_id' to get 'country' and 'bid_id'
joined = pd.merge(union_df, Source3_35_0[['bidder_id', 'bid_id', 'country']], on='bidder_id', how='inner')

# Group by the composite key and aggregate count of bids
grouped = joined.groupby(
    ['bidder_id', 'payment_account', 'address', 'outcome', 'country'],
    dropna=False,  # keep NaN in group keys if any
    as_index=False
).agg(bids_count=('bid_id', 'count'))

# Ensure correct dtypes
grouped['bids_count'] = grouped['bids_count'].astype(int)
grouped['outcome'] = pd.to_numeric(grouped['outcome'], errors='coerce')

# Reorder columns to match target schema
result = grouped[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)