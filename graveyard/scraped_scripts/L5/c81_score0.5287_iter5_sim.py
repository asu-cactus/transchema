import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_4.csv", index_col=0)

merged = df4.merge(df1[['Ord_id', 'Order_ID']], on='Ord_id', how='left')
merged = merged.merge(df3[['Order_ID', 'Ship_Mode']], on='Order_ID', how='left')
merged = merged.merge(df0[['Prod_id', 'Product_Category']], on='Prod_id', how='left')
merged = merged.merge(df2[['Cust_id', 'Region']], on='Cust_id', how='left')

pivot = merged.pivot_table(index='Product_Category', columns='Region', values='Sales', aggfunc='sum')

result = pivot.sum(axis=1).reset_index(name='Sales')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_81/target_multisource_mcts.csv", index=False)