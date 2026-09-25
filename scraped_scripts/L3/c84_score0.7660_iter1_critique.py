import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

# UNION Source0 and Source1 (Source1 has no 'outcome', so add it with NaN or 0)
df1['outcome'] = 0.0  # Since Source1 has no outcome, fill with 0.0 to match schema
unioned = pd.concat([df0, df1], ignore_index=True)

# Join unioned with Source2 on bidder_id to get country
joined = unioned.merge(df2[['bidder_id', 'country']], on='bidder_id', how='left')

# Count bids per bidder from Source2
bids_count = df2.groupby('bidder_id').size().reset_index(name='bids_count')

# Join bids_count to joined data on bidder_id
joined = joined.merge(bids_count, on='bidder_id', how='left')

# Group by bidder_id, payment_account, address, country
# Aggregate outcome by mean, bids_count by sum
result = joined.groupby(['bidder_id', 'payment_account', 'address', 'country'], as_index=False).agg({
    'outcome': 'mean',
    'bids_count': 'sum'
})

# Ensure bids_count is int
result['bids_count'] = result['bids_count'].fillna(0).astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)