import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

df0['Ord_id'] = df0['Ord_id'].str.replace('Ord_', '').astype(int)
df1['Ship_id'] = df1['Ship_id'].str.replace('SHP_', '').astype(int)
df2['Cust_id'] = df2['Cust_id'].str.replace('Cust_', '').astype(int)
df3['Prod_id'] = df3['Prod_id'].str.replace('Prod_', '').astype(int)
df4['Ord_id'] = df4['Ord_id'].str.replace('Ord_', '').astype(int)
df4['Prod_id'] = df4['Prod_id'].str.replace('Prod_', '').astype(int)
df4['Ship_id'] = df4['Ship_id'].str.replace('SHP_', '').astype(int)
df4['Cust_id'] = df4['Cust_id'].str.replace('Cust_', '').astype(int)

merged_0 = pd.merge(df4, df0[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')
merged_1 = pd.merge(merged_0, df1[['Ship_id']], on='Ship_id', how='inner')
merged_2 = pd.merge(merged_1, df2[['Cust_id']], on='Cust_id', how='inner')
merged_3 = pd.merge(merged_2, df3[['Prod_id']], on='Prod_id', how='inner')

result = merged_3[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Date'] = result['Order_Date'].astype(str)

result['Ord_id'] = result['Ord_id'].astype(int)
result['Prod_id'] = result['Prod_id'].astype(int)
result['Ship_id'] = result['Ship_id'].astype(int)
result['Cust_id'] = result['Cust_id'].astype(int)
result['Sales'] = result['Sales'].round().astype(int)
result['Discount'] = (result['Discount'] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)