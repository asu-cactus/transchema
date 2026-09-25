import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

agg = df0.groupby(['bidder_id', 'payment_account', 'address'], as_index=False).agg(
    bids_count=('payment_account', 'count'),
    outcome=('outcome', 'mean')
)

agg['bidder_id'] = agg['bidder_id'].astype(str)
agg['payment_account'] = agg['payment_account'].astype(str)
agg['address'] = agg['address'].astype(str)
agg['bids_count'] = agg['bids_count'].astype(int)
agg['outcome'] = agg['outcome'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)