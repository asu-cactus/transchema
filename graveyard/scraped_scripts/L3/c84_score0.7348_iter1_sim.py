import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

df01 = pd.concat([df0, df1], ignore_index=True)

pivot = df01.pivot_table(index=['bidder_id', 'payment_account', 'address'], values='outcome', aggfunc='mean').reset_index()

merged = pivot.merge(df2[['bidder_id', 'country']], on='bidder_id', how='left')

bids_count = df2.groupby('bidder_id').size().reset_index(name='bids_count')

result = merged.merge(bids_count, on='bidder_id', how='left')

result = result[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result['bids_count'] = result['bids_count'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)