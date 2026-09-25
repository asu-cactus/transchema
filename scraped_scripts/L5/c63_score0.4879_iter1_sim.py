import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

unpivoted = df4.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=['Sales', 'Discount'], var_name='variable', value_name='value')

pivot_sales = unpivoted[unpivoted['variable'] == 'Sales'].copy()
pivot_discount = unpivoted[unpivoted['variable'] == 'Discount'].copy()

pivot_sales = pivot_sales.rename(columns={'value': 'Sales'}).drop(columns=['variable'])
pivot_discount = pivot_discount.rename(columns={'value': 'Discount'}).drop(columns=['variable'])

merged = pd.merge(pivot_sales, pivot_discount, on=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], how='inner')

merged = merged.astype({'Sales': 'int64', 'Discount': 'int64'})

merged = pd.merge(merged, df0[['Ord_id']], on='Ord_id', how='left')
merged = pd.merge(merged, df1[['Cust_id']], on='Cust_id', how='left')
merged = pd.merge(merged, df2[['Prod_id']], on='Prod_id', how='left')
merged = pd.merge(merged, df3[['Ship_id']], on='Ship_id', how='left')

result = merged[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)