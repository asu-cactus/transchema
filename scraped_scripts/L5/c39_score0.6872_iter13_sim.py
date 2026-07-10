import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

s0['Prod_id'] = s0['Prod_id'].str.replace('Prod_', '').astype(int)
s0['Ship_id'] = s0['Ship_id'].str.replace('SHP_', '').astype(int)
s0['Cust_id'] = s0['Cust_id'].str.replace('Cust_', '').astype(int)

grouped = s0.groupby(['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).first()

s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '').astype(int)

merged = pd.merge(grouped, s4[['Prod_id', 'Product_Category']], on='Prod_id', how='left')

result = merged[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)