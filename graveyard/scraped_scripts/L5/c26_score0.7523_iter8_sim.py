import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

join_1_2 = pd.merge(s1, s2, left_on='Ord_id', right_on='Ord_id', how='inner')
join_1_2_4 = pd.merge(join_1_2, s4, left_on='Prod_id', right_on='Prod_id', how='inner')
join_all = pd.merge(join_1_2_4, s0, left_on='Ship_id', right_on='Ship_id', how='inner')

result = join_all[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)