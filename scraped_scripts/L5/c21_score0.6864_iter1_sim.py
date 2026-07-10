import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

s2['Ord_id'] = s2['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s2['Prod_id'] = s2['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s2['Cust_id'] = s2['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)

s0['Cust_id'] = s0['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
s1['Prod_id'] = s1['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s3['Ship_id'] = s3['Ship_id'].str.replace('SHP_', '', regex=False)
s2['Ship_id'] = s2['Ship_id'].str.replace('SHP_', '', regex=False)

pivot_result = s2[['Ord_id', 'Prod_id', 'Cust_id', 'Ship_id', 'Sales', 'Discount']]

pivot_result = pivot_result.merge(s4[['Ord_id', 'Order_Priority']], on='Ord_id', how='left')
pivot_result = pivot_result.merge(s0[['Cust_id']], on='Cust_id', how='left')
pivot_result = pivot_result.merge(s1[['Prod_id']], on='Prod_id', how='left')
pivot_result = pivot_result.merge(s3[['Ship_id']], on='Ship_id', how='left')

pivot_result = pivot_result[['Ship_id', 'Order_Priority', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales', 'Discount']]

pivot_result['Ship_id'] = 'SHP_' + pivot_result['Ship_id'].astype(str)
pivot_result['Order_Priority'] = pivot_result['Order_Priority'].astype(str)
pivot_result['Ord_id'] = pivot_result['Ord_id'].astype(int)
pivot_result['Prod_id'] = pivot_result['Prod_id'].astype(int)
pivot_result['Cust_id'] = pivot_result['Cust_id'].astype(int)
pivot_result['Sales'] = pivot_result['Sales'].round().astype(int)
pivot_result['Discount'] = (pivot_result['Discount'] * 100).round().astype(int)

pivot_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)