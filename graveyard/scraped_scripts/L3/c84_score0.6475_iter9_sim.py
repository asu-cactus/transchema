import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

union_result = pd.concat([source0, source1], ignore_index=True, sort=False)

merged = union_result.merge(source2[['bidder_id', 'country']], on='bidder_id', how='left')

merged['outcome'] = pd.to_numeric(merged['outcome'], errors='coerce')
merged['bids_count'] = 1

final = merged[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)