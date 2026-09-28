import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

df1['outcome'] = pd.NA
union_df = pd.concat([df0, df1], ignore_index=True, sort=False)

merged = union_df.merge(df2[['bidder_id', 'bid_id']], on='bidder_id', how='left')

result = merged.groupby(['bidder_id', 'payment_account', 'address', 'outcome'], dropna=False).agg(bids_count=('bid_id', 'count')).reset_index()

result['outcome'] = result['outcome'].astype(float)
result['bids_count'] = result['bids_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)