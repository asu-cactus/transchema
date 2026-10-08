import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, on=['bidder_id', 'payment_account', 'address'], how='outer')

merged = pd.merge(source0, join_1_2, on='bidder_id', how='inner')

merged['bids_count'] = merged.groupby('bidder_id')['bid_id'].transform('count')

result = merged[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)