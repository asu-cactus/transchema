import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

s0['Prod_id'] = s0['Prod_id'].str.replace('Prod_', '').astype(int)
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '').astype(int)

pivot = s0.pivot_table(index=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], 
                       values='Sales', aggfunc='sum').reset_index()

result = pivot.merge(s4[['Prod_id', 'Product_Category']], on='Prod_id', how='left')

result = result[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result['Ord_id'] = result['Ord_id'].astype(str)
result['Ship_id'] = result['Ship_id'].astype(str)
result['Cust_id'] = result['Cust_id'].astype(str)
result['Product_Category'] = result['Product_Category'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)