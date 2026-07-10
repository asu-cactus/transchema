import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

pivot_result = df1.groupby('Ship_id').first().reset_index()

merged = pd.merge(pivot_result[['Ship_id']], df2, on='Ship_id', how='inner')

merged['Ord_id'] = merged['Ord_id'].str.replace('Ord_', '').astype(int)
merged['Prod_id'] = merged['Prod_id'].str.replace('Prod_', '').astype(int)
merged['Cust_id'] = merged['Cust_id'].str.replace('Cust_', '').astype(int)

result = merged[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)