import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

join_df = pd.merge(s0, s2, left_on='bidder_id', right_on='bidder_id', how='inner', suffixes=('_0', '_2'))
union_df = pd.concat([s0, s1], ignore_index=True, sort=False)

union_df['bids_count'] = 1
union_df['outcome'] = union_df['outcome'].astype(float) if 'outcome' in union_df else pd.Series(dtype=float)
union_df['address'] = union_df['address'].astype(str)

union_df = union_df[['bidder_id', 'payment_account', 'address', 'outcome', 'bids_count']]

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)