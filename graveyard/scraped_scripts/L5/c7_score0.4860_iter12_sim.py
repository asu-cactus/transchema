import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

merged = pd.merge(source4, source0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='left')

result = merged[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Quantity'] = pd.to_numeric(result['Order_Quantity'], errors='coerce').fillna(0).astype(int)
result['Ord_id'] = result['Ord_id'].str.extract('(\d+)').astype(float).astype('Int64')
result['Prod_id'] = result['Prod_id'].str.extract('(\d+)').astype(float).astype('Int64')
result['Ship_id'] = result['Ship_id'].str.extract('(\d+)').astype(float).astype('Int64')
result['Cust_id'] = result['Cust_id'].str.extract('(\d+)').astype(float).astype('Int64')
result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)