import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

join1 = pd.merge(source4, source0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='inner')
join2 = pd.merge(join1, source1[['Cust_id']], on='Cust_id', how='inner')
join3 = pd.merge(join2, source2[['Ord_id']], on='Ord_id', how='inner')
join4 = pd.merge(join3, source3[['Ship_id']], on='Ship_id', how='inner')

result = join4[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Quantity'] = result['Order_Quantity'].astype(int)
result['Ord_id'] = result['Ord_id'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(str)
result['Ship_id'] = result['Ship_id'].astype(str)
result['Cust_id'] = result['Cust_id'].astype(str)
result['Sales'] = result['Sales'].astype(float).round().astype(int)
result['Discount'] = (result['Discount'] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)