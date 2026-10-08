import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

s1['Prod_id'] = s1['Prod_id'].astype(str)
s4['Prod_id'] = s4['Prod_id'].astype(str)
join_1 = pd.merge(s1, s4, on='Prod_id', how='inner')

join_1['Ord_id'] = join_1['Ord_id'].astype(str)
s2['Ord_id'] = s2['Ord_id'].astype(str)
join_2 = pd.merge(join_1, s2[['Order_Date', 'Ord_id']], on='Ord_id', how='inner')

join_2['Ship_id'] = join_2['Ship_id'].astype(str)
s0['Ship_id'] = s0['Ship_id'].astype(str)
join_3 = pd.merge(join_2, s0[['Ship_id']], on='Ship_id', how='inner')

join_3['Cust_id'] = join_3['Cust_id'].astype(str)
s3['Cust_id'] = s3['Cust_id'].astype(str)
join_4 = pd.merge(join_3, s3[['Cust_id']], on='Cust_id', how='inner')

result = join_4[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '').astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)
result['Sales'] = result['Sales'].round().astype(int)
result['Order_Date'] = result['Order_Date'].astype(str)
result['Product_Sub_Category'] = result['Product_Sub_Category'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)