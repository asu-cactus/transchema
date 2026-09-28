import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

# Add 'outcome' column to df1 with default 0.0 to match df0 schema for union
df1['outcome'] = 0.0

# UNION df0 and df1 (concatenate)
df_union = pd.concat([df0, df1], ignore_index=True, sort=False)

# Group by bidder_id, payment_account, address and sum outcome
agg_outcome = df_union.groupby(['bidder_id', 'payment_account', 'address'], dropna=False).agg({'outcome': 'sum'}).reset_index()

# Compute bids_count from df2 grouped by bidder_id
bids_count = df2.groupby('bidder_id').size().rename('bids_count').reset_index()

# Join aggregated outcome with bids_count on bidder_id
result = pd.merge(agg_outcome, bids_count, on='bidder_id', how='left')

# Fill missing bids_count with 0 and convert to int
result['bids_count'] = result['bids_count'].fillna(0).astype(int)

# Ensure columns are in target schema order
result = result[['bidder_id', 'payment_account', 'address', 'outcome', 'bids_count']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)