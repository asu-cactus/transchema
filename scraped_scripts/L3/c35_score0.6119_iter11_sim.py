import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)
union_result = pd.concat([source1, source2], ignore_index=True)

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)

joined = pd.merge(union_result, source0[['bidder_id', 'country']], on='bidder_id', how='left')

bids_count = source0.groupby('bidder_id').size().rename('bids_count')

result = joined.merge(bids_count, left_on='bidder_id', right_index=True, how='left')

result = result[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result['bids_count'] = result['bids_count'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)