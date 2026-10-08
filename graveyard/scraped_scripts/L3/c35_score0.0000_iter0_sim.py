import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, how='inner', on=['bidder_id', 'payment_account', 'address'])

final_join = pd.merge(join_1_2, source0[['bidder_id', 'country']], how='left', on='bidder_id')

final = final_join[['bidder_id', 'payment_account', 'address', 'outcome', 'country']].copy()

bids_count = source0.groupby('bidder_id').size().rename('bids_count')

final = final.merge(bids_count, how='left', left_on='bidder_id', right_index=True)

final['bids_count'] = final['bids_count'].fillna(0).astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)