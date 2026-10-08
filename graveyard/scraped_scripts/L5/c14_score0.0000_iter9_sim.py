import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['Cust_id'], value_vars=['Customer_Name', 'Province', 'Region', 'Customer_Segment'], var_name='Attribute', value_name='Ship_id')
df0_unpivot = df0_unpivot[['Ship_id', 'Cust_id']].dropna()

df2['Ord_id'] = df2['Ord_id'].str.replace('Ord_', '').astype(int)
df2['Prod_id'] = df2['Prod_id'].str.replace('Prod_', '').astype(int)
df2['Cust_id'] = df2['Cust_id'].str.replace('Cust_', '').astype(int)

df0_unpivot['Cust_id'] = df0_unpivot['Cust_id'].str.replace('Cust_', '').astype(int)

merged = pd.merge(df0_unpivot, df2, on=['Ship_id', 'Cust_id'], how='inner')

result = merged[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)