import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

agg_source2 = source2.groupby(['bidder_id', 'country'], as_index=False).agg(bids_count=('bid_id', 'count'))

join_0 = pd.merge(agg_source2, source0, how='left', on='bidder_id')

join_1 = pd.merge(join_0, source1, how='left', on='bidder_id', suffixes=('', '_s1'))

join_1['payment_account'] = join_1['payment_account'].combine_first(join_1['payment_account_s1'])
join_1['address'] = join_1['address'].combine_first(join_1['address_s1'])

result = join_1[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)