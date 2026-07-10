import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_84/training_2.csv", index_col=0)

agg_src2 = src2.groupby(['bidder_id', 'country']).agg(
    bids_count=pd.NamedAgg(column='auction', aggfunc=lambda x: x.nunique())
).reset_index()

join_0 = pd.merge(agg_src2, src0, how='left', on='bidder_id')
join_1 = pd.merge(join_0, src1, how='left', on='bidder_id', suffixes=('', '_src1'))

result = join_1[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_84/target_multisource_mcts.csv", index=False)