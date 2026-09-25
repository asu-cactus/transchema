import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

agg_0 = source0.groupby('bidder_id', as_index=False).agg(bids_count=('bid_id', 'count'), country=('country', 'first'))

join_1 = pd.merge(agg_0, source1, on='bidder_id', how='inner')

join_2 = pd.merge(join_1, source2[['bidder_id', 'outcome']], on='bidder_id', how='left')

result = join_2[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)