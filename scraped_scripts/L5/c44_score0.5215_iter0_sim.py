import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

grouped_source1 = source1.groupby('Customer_Segment', as_index=False).agg({'Cust_id': 'first'})

merged = pd.merge(grouped_source1, source4, on='Cust_id', how='inner')

result = merged[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)