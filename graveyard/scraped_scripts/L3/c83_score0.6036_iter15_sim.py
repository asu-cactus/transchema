import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

df1['outcome'] = pd.NA
union_result = pd.concat([df0, df1], ignore_index=True, sort=False)

merged = union_result.merge(df2[['bidder_id']], on='bidder_id', how='left')

merged['bids_count'] = merged.groupby('bidder_id')['bidder_id'].transform('count')

result = merged[['bidder_id', 'payment_account', 'address', 'outcome', 'bids_count']].copy()

result['bidder_id'] = result['bidder_id'].astype(str)
result['payment_account'] = result['payment_account'].astype(str)
result['address'] = result['address'].astype(str)
result['outcome'] = pd.to_numeric(result['outcome'], errors='coerce')
result['bids_count'] = result['bids_count'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)