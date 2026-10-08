import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

s0['Prod_id'] = s0['Prod_id'].str.replace('Prod_', '').astype(int)
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '').astype(int)

merged = pd.merge(s0, s4[['Product_Category', 'Prod_id']], on='Prod_id', how='left')

result = merged[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result['Ord_id'] = result['Ord_id'].astype(str)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)