import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)

source0['Ord_id'] = source0['Ord_id'].str.replace('Ord_', '').astype(int)
source0['Prod_id'] = source0['Prod_id'].str.replace('Prod_', '').astype(int)
source0['Cust_id'] = source0['Cust_id'].str.replace('Cust_', '').astype(int)

grouped = source0.groupby(['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id'], as_index=False).agg({'Sales':'sum'})

source1['Prod_id'] = source1['Prod_id'].str.replace('Prod_', '').astype(int)

merged = pd.merge(grouped, source1[['Prod_id', 'Product_Category']], on='Prod_id', how='left')

result = merged[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)