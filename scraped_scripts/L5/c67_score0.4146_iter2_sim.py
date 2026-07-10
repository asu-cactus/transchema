import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

s1_renamed = s1.copy()
s1_renamed['Ship_id'] = s1_renamed['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

s2_renamed = s2.copy()
s2_renamed['Ship_id'] = s2_renamed['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s2_renamed['Ord_id'] = s2_renamed['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s2_renamed['Cust_id'] = s2_renamed['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

union_1_2 = pd.concat([s1_renamed, s2_renamed], ignore_index=True, sort=False)

join_1 = union_1_2.merge(s0[['Prod_id']], on='Prod_id', how='inner')

s3_renamed = s3.copy()
s3_renamed['Cust_id'] = s3_renamed['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

join_2 = join_1.merge(s3_renamed[['Cust_id']], on='Cust_id', how='inner')

s4_renamed = s4.copy()
s4_renamed['Ord_id'] = s4_renamed['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)

final_join = join_2.merge(s4_renamed[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

result = final_join.rename(columns={'Order_Date': 'Ship_Date'})

result = result[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)