import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

# Join df2 with df0 on Prod_id
join_0 = df2.merge(df0, on='Prod_id', how='inner')

# Join with df1 on Ship_id
join_1 = join_0.merge(df1, on='Ship_id', how='inner')

# Join with df3 on Ord_id
join_2 = join_1.merge(df3, on='Ord_id', how='inner')

# Join with df4 on Cust_id
join_3 = join_2.merge(df4, on='Cust_id', how='inner')

# Group by Prod_id and sum Profit
grouped = join_3.groupby('Prod_id', as_index=False).agg({'Profit': 'sum'})

# Project only Profit column (target schema only has Profit)
result = grouped[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)