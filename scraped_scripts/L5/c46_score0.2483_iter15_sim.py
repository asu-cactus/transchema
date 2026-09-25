import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

union_2_4 = pd.concat([s2, s4], ignore_index=True, sort=False)

join_1 = union_2_4.merge(s0[['Customer_Name', 'Cust_id']], on='Cust_id', how='left')

join_2 = join_1.merge(s3[['Prod_id']], on='Prod_id', how='left')

join_3 = join_2.merge(s1[['Ship_id']], on='Ship_id', how='left')

result = join_3[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']].copy()

result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '').astype('Int64')
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype('Int64')
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)