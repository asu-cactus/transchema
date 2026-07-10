import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

union_result = pd.concat([source4, source4], ignore_index=True)

merged = pd.merge(union_result, source0, left_on='Prod_id', right_on='Prod_id')

result = merged[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].copy()

result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)
result['Ord_id'] = result['Ord_id'].astype(str)
result['Product_Category'] = result['Product_Category'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)