import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

# Union source0 and source1 on common columns: bidder_id, payment_account, address
# source0 has 'outcome', source1 does not, so add 'outcome' column with NaN to source1 before union
source1['outcome'] = pd.NA
union_0_1 = pd.concat([
    source0[['bidder_id', 'payment_account', 'address', 'outcome']],
    source1[['bidder_id', 'payment_account', 'address', 'outcome']]
], ignore_index=True)

# Join unioned table with source2 on bidder_id to get country and bid_id
joined = pd.merge(union_0_1, source2[['bidder_id', 'country', 'bid_id']], on='bidder_id', how='inner')

# Group by bidder_id, payment_account, address, country
grouped = joined.groupby(
    ['bidder_id', 'payment_account', 'address', 'country'], dropna=False, as_index=False
).agg(
    outcome=('outcome', 'sum'),
    bids_count=('bid_id', 'count')
)

# Cast types to match target schema
grouped['outcome'] = grouped['outcome'].astype(float)
grouped['bids_count'] = grouped['bids_count'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)