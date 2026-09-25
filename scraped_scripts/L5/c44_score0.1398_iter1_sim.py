import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

union_result = pd.concat([s1, s4], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, s2[['Prod_id']], on='Prod_id', how='inner')

join_result_2 = pd.merge(join_result_1, s3[['Ship_id']], on='Ship_id', how='inner')

target = join_result_2[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)