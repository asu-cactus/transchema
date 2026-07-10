import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)

source0['Sales'] = pd.to_numeric(source0['Sales'], errors='coerce')
agg_source0 = source0.groupby(['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id'], as_index=False)['Sales'].sum()

merged = pd.merge(agg_source0, source1[['Product_Category', 'Prod_id']], on='Prod_id', how='left')

merged['Ord_id'] = merged['Ord_id'].str.replace('Ord_', '').astype(int)
merged['Prod_id'] = merged['Prod_id'].str.replace('Prod_', '').astype(int)
merged['Cust_id'] = merged['Cust_id'].str.replace('Cust_', '').astype(int)
merged['Ship_id'] = merged['Ship_id'].astype(str)
merged['Product_Category'] = merged['Product_Category'].astype(str)
merged['Sales'] = merged['Sales'].round().astype(int)

result = merged[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)