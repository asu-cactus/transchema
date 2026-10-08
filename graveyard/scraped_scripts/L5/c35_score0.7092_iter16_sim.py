import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

df0['Cust_id'] = df0['Cust_id'].str.strip()
df3['Cust_id'] = df3['Cust_id'].str.strip()
df1['Prod_id'] = df1['Prod_id'].str.strip()
df0['Prod_id'] = df0['Prod_id'].str.strip()
df0['Ship_id'] = df0['Ship_id'].str.strip()
df2['Ship_id'] = df2['Ship_id'].str.strip()
df0['Ord_id'] = df0['Ord_id'].str.strip()
df4['Ord_id'] = df4['Ord_id'].str.strip()

join_result_0 = pd.merge(df0, df3, how='inner', on='Cust_id')
join_result_1 = pd.merge(join_result_0, df1, how='inner', on='Prod_id')
join_result_2 = pd.merge(join_result_1, df2, how='inner', on='Ship_id')
join_result_3 = pd.merge(join_result_2, df4, how='inner', on='Ord_id')

result = join_result_3[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']].copy()

result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '').astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)
result['Sales'] = result['Sales'].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)