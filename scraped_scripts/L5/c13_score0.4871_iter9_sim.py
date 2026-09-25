import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

unpivoted = source1.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=['Sales', 'Discount'], var_name='Measure', value_name='Value')

joined_1 = pd.merge(unpivoted, source3[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='left')
joined_2 = pd.merge(joined_1, source0[['Ord_id']], on='Ord_id', how='left')
joined_3 = pd.merge(joined_2, source4[['Ship_id']], on='Ship_id', how='left')
joined_4 = pd.merge(joined_3, source2[['Cust_id']], on='Cust_id', how='left')

pivoted = joined_4.pivot_table(index=['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], columns='Measure', values='Value', aggfunc='sum').reset_index()

pivoted['Sales'] = pivoted['Sales'].fillna(0).round().astype(int)
pivoted['Discount'] = pivoted['Discount'].fillna(0).round().astype(int)

pivoted = pivoted[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)