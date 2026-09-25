import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

# Join df0 and df2 on Prod_id
df_0_2 = pd.merge(df0, df2, left_on='Prod_id', right_on='Prod_id', how='inner')

# Join df1 and df_0_2 on Ship_id
df_1_0_2 = pd.merge(df1, df_0_2, left_on='Ship_id', right_on='Ship_id', how='inner')

# Join df3 and df_1_0_2 on Ord_id (note df3 has Ord_id, df2 has Ord_id)
df_3_1_0_2 = pd.merge(df3, df_1_0_2, left_on='Ord_id', right_on='Ord_id', how='inner')

# Join df4 and df_3_1_0_2 on Cust_id
df_all = pd.merge(df4, df_3_1_0_2, left_on='Cust_id', right_on='Cust_id', how='inner')

# Select Profit column and ensure float type
result = df_all[['Profit']].copy()
result['Profit'] = pd.to_numeric(result['Profit'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)