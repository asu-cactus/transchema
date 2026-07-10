import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

merged = pd.merge(source4, source0[['Product_Sub_Category', 'Prod_id']], on='Prod_id', how='left')

result = merged[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Quantity'] = result['Order_Quantity'].astype('Int64')
result['Sales'] = result['Sales'].round().astype('Int64')
result['Discount'] = (result['Discount'] * 100).round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)