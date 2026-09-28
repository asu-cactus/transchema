import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

union_source = pd.concat([source0, source1], ignore_index=True)

merged = pd.merge(union_source, source2[['bidder_id', 'country']], on='bidder_id', how='inner')

merged['outcome'] = merged['outcome'].astype(float)
merged['bids_count'] = 1

target = merged[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)