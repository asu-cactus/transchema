import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

joined = pd.merge(source0, source2, left_on='bidder_id', right_on='bidder_id', how='inner', suffixes=('_0', '_2'))

agg = joined.groupby('bidder_id').agg(
    payment_account=('payment_account', 'first'),
    address=('address', 'first'),
    outcome=('outcome', 'first'),
    bids_count=('bid_id', 'count')
).reset_index()

agg['payment_account'] = agg['payment_account'].astype(str)
agg['address'] = agg['address'].astype(str)
agg['bidder_id'] = agg['bidder_id'].astype(str)
agg['outcome'] = pd.to_numeric(agg['outcome'], errors='coerce')
agg['bids_count'] = agg['bids_count'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)