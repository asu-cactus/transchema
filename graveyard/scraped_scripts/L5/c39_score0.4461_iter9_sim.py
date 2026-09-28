import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

id_vars = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']
value_vars = ['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin']

unpivoted = source0.melt(id_vars=id_vars, value_vars=value_vars, var_name='Measure', value_name='Value')

source4['Prod_id'] = source4['Prod_id'].astype(str)
unpivoted['Prod_id'] = unpivoted['Prod_id'].astype(str)

joined = pd.merge(unpivoted, source4[['Prod_id', 'Product_Category']], on='Prod_id', how='left')

result = joined[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)