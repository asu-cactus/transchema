import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

pivot_df = df2[['Ship_Mode', 'Ship_id']].drop_duplicates()

merged = pd.merge(pivot_df, df4, on='Ship_id', how='inner')
merged = pd.merge(merged, df0[['Ord_id']], on='Ord_id', how='inner')
merged = pd.merge(merged, df1[['Cust_id']], on='Cust_id', how='inner')
merged = pd.merge(merged, df3[['Prod_id']], on='Prod_id', how='inner')

result = merged[['Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']].copy()

result['Sales'] = result['Sales'].round().astype('Int64')
result['Ord_id'] = result['Ord_id'].str.extract('(\d+)').astype('Int64')
result['Prod_id'] = result['Prod_id'].str.extract('(\d+)').astype('Int64')
result['Ship_id'] = result['Ship_id'].str.extract('(\d+)').astype('Int64')
result['Cust_id'] = result['Cust_id'].str.extract('(\d+)').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)