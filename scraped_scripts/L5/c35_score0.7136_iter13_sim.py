import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

df0['Ord_id'] = df0['Ord_id'].str.replace('Ord_', '').astype(int)
df0['Prod_id'] = df0['Prod_id'].str.replace('Prod_', '').astype(int)
df0['Cust_id'] = df0['Cust_id'].str.replace('Cust_', '').astype(int)

df1['Prod_id'] = df1['Prod_id'].str.replace('Prod_', '').astype(int)

df3['Cust_id'] = df3['Cust_id'].str.replace('Cust_', '').astype(int)

df4['Ord_id'] = df4['Ord_id'].str.replace('Ord_', '').astype(int)

join_0 = pd.merge(df0, df1[['Product_Category', 'Prod_id']], on='Prod_id', how='left')
join_1 = pd.merge(join_0, df3[['Cust_id']], on='Cust_id', how='left')
join_2 = pd.merge(join_1, df4[['Ord_id']], on='Ord_id', how='left')

result = join_2[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)