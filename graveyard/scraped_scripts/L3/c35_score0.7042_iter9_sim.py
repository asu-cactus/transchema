import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

joined_0_2 = pd.merge(source0[['bidder_id', 'country']], source2, on='bidder_id', how='inner')

union_1_2 = pd.concat([source1, source2], ignore_index=True, sort=False)

merged = pd.merge(joined_0_2, union_1_2, on='bidder_id', how='left', suffixes=('_left', ''))

result = pd.DataFrame()
result['bidder_id'] = merged['bidder_id']
result['payment_account'] = merged['payment_account']
result['address'] = merged['address']
result['outcome'] = pd.to_numeric(merged['outcome'], errors='coerce').astype(float)
result['country'] = merged['country']
result['bids_count'] = 1

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)