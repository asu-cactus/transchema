import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

df1['Ship_id'] = df1['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
pivot_result = df1[['Ship_Date', 'Ship_id']]

df2['Ship_id'] = df2['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
df2['Ord_id'] = df2['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df2['Cust_id'] = df2['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

join_result_1 = pd.merge(pivot_result, df2, on='Ship_id', how='inner')

join_result_1 = join_result_1.drop(columns=['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin'])

join_result_2 = pd.merge(join_result_1, df0[['Prod_id']], on='Prod_id', how='inner')

df3['Cust_id'] = df3['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
join_result_3 = pd.merge(join_result_2, df3[['Cust_id']], on='Cust_id', how='inner')

df4['Ord_id'] = df4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
join_result_4 = pd.merge(join_result_3, df4[['Ord_id']], on='Ord_id', how='inner')

result = join_result_4[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)