import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

join_result = pd.merge(source1, source2[['bidder_id', 'country']], on='bidder_id', how='inner')

join_result['outcome'] = pd.NA
join_result = join_result[['bidder_id', 'payment_account', 'address', 'outcome', 'country']]

union_df = pd.concat([source0, join_result], ignore_index=True, sort=False)

union_df['outcome'] = pd.to_numeric(union_df['outcome'], errors='coerce')

agg = union_df.groupby(['bidder_id', 'payment_account', 'address', 'country'], dropna=False).agg(
    outcome=('outcome', 'sum'),
    bids_count=('bidder_id', 'count')
).reset_index()

agg['outcome'] = agg['outcome'].astype(float)
agg['bids_count'] = agg['bids_count'].astype(int)

agg = agg[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)