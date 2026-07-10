import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

join_0_2 = pd.merge(source0, source2, on="bidder_id", how="inner", suffixes=('_0', '_2'))
join_all = pd.merge(join_0_2, source1, on="bidder_id", how="inner", suffixes=('', '_1'))

grouped = join_all.groupby(
    ['bidder_id', 'payment_account', 'address', 'outcome', 'country'], dropna=False, as_index=False
).agg(bids_count=('bid_id', 'count'))

grouped['bidder_id'] = grouped['bidder_id'].astype(str)
grouped['payment_account'] = grouped['payment_account'].astype(str)
grouped['address'] = grouped['address'].astype(str)
grouped['outcome'] = pd.to_numeric(grouped['outcome'], errors='coerce')
grouped['country'] = grouped['country'].astype(str)
grouped['bids_count'] = grouped['bids_count'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)