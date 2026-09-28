import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

join_result = pd.merge(source1, source2[['bidder_id']], on='bidder_id', how='inner')

union_df = pd.concat([source0, join_result], ignore_index=True, sort=False)

agg = union_df.groupby(['bidder_id', 'payment_account', 'address'], as_index=False).agg(
    outcome=('outcome', 'sum'),
    bids_count=('bidder_id', 'count')
)

agg['outcome'] = agg['outcome'].astype(float)
agg['bids_count'] = agg['bids_count'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)