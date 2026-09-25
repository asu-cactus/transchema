import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

s0['Ord_id'] = s0['Ord_id'].astype(str)
s4['Ord_id'] = s4['Ord_id'].astype(str)

pivot = s4[['Ord_id', 'Order_Priority']].drop_duplicates()

joined_0 = pd.merge(pivot, s0, on='Ord_id', how='inner')

joined_1 = pd.merge(joined_0, s2[['Cust_id']], on='Cust_id', how='inner')

joined_1['Ord_id'] = joined_1['Ord_id'].str.replace('Ord_', '').astype(int)
joined_1['Ship_id'] = joined_1['Ship_id'].str.replace('SHP_', '').astype(int)
joined_1['Cust_id'] = joined_1['Cust_id'].str.replace('Cust_', '').astype(int)
joined_1['Prod_id'] = joined_1['Prod_id'].astype(str)
joined_1['Order_Priority'] = joined_1['Order_Priority'].astype(str)
joined_1['Sales'] = joined_1['Sales'].round().astype(int)
joined_1['Discount'] = (joined_1['Discount'] * 100).round().astype(int)

result = joined_1[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)