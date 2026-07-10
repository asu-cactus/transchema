import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

join_result = pd.merge(source1, source2, on=['bidder_id', 'payment_account', 'address'], how='outer')

source0_renamed = source0.rename(columns={'country': 'country'})
source0_selected = source0_renamed[['bidder_id', 'country']].copy()
source0_selected['outcome'] = 0.0
source0_selected['payment_account'] = None
source0_selected['address'] = None
source0_selected['bids_count'] = 1

join_result['bids_count'] = 1
join_result['country'] = None
join_result['outcome'] = join_result['outcome'].astype(float)

join_result = join_result[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

source0_selected = source0_selected[['bidder_id', 'payment_account', 'address', 'outcome', 'country', 'bids_count']]

target = pd.concat([source0_selected, join_result], ignore_index=True)

target['bids_count'] = target['bids_count'].astype('Int64')

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)