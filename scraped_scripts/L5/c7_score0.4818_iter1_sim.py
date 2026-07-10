import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

join1 = pd.merge(df4, df0[['Product_Sub_Category', 'Prod_id']], how='inner', left_on='Prod_id', right_on='Prod_id')
join2 = pd.merge(join1, df1[['Cust_id']], how='inner', left_on='Cust_id', right_on='Cust_id')
join3 = pd.merge(join2, df3[['Ship_id']], how='inner', left_on='Ship_id', right_on='Ship_id')
join4 = pd.merge(join3, df2[['Ord_id']], how='inner', left_on='Ord_id', right_on='Ord_id')

result = join4[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Quantity'] = result['Order_Quantity'].astype(int)
result['Ord_id'] = result['Ord_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
result['Prod_id'] = result['Prod_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
result['Ship_id'] = result['Ship_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
result['Cust_id'] = result['Cust_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
result['Sales'] = result['Sales'].round().astype(int)
result['Discount'] = (result['Discount'] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)