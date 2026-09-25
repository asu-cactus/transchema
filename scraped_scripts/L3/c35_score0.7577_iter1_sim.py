import pandas as pd

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)
union_result = pd.concat([s1, s2], ignore_index=True, sort=False)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)

joined = pd.merge(union_result, s0[['bidder_id', 'bid_id', 'country']], on='bidder_id', how='left')

agg = joined.groupby(['bidder_id', 'payment_account', 'address', 'outcome', 'country'], dropna=False).agg(bids_count=('bid_id', 'count')).reset_index()

agg['outcome'] = agg['outcome'].astype(float)
agg['bids_count'] = agg['bids_count'].astype(int)
agg['bidder_id'] = agg['bidder_id'].astype(str)
agg['payment_account'] = agg['payment_account'].astype(str)
agg['address'] = agg['address'].astype(str)
agg['country'] = agg['country'].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)