import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

# UNION Source3_84_0 and Source3_84_1 (same schema)
unioned_bidder_info = pd.concat([source0, source1], ignore_index=True)

# JOIN unioned bidder info with Source3_84_2 on bidder_id
joined = pd.merge(unioned_bidder_info, source2, on="bidder_id", how="inner")

# GROUP BY bidder_id, payment_account, address, country
# Aggregate outcome by mean, bids_count by count of bid_id
grouped = joined.groupby(
    ['bidder_id', 'payment_account', 'address', 'country'], dropna=False, as_index=False
).agg(
    outcome=('outcome', 'mean'),
    bids_count=('bid_id', 'count')
)

# Ensure correct dtypes
grouped['bidder_id'] = grouped['bidder_id'].astype(str)
grouped['payment_account'] = grouped['payment_account'].astype(str)
grouped['address'] = grouped['address'].astype(str)
grouped['outcome'] = pd.to_numeric(grouped['outcome'], errors='coerce')
grouped['country'] = grouped['country'].astype(str)
grouped['bids_count'] = grouped['bids_count'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)