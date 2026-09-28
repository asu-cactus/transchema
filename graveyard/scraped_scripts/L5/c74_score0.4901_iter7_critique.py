import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)

# Join df4 with df1 on Ord_id
df = pd.merge(df4, df1, on='Ord_id', how='inner')

# Join with df0 on Prod_id
df = pd.merge(df, df0, on='Prod_id', how='inner')

# Join with df3 on Ship_id
df = pd.merge(df, df3, on='Ship_id', how='inner')

# Join with df2 on Cust_id
df = pd.merge(df, df2, on='Cust_id', how='inner')

# Group by Product_Category and Order_Priority, aggregate sum of Profit
df_grouped = df.groupby(['Product_Category', 'Order_Priority'], as_index=False).agg({'Profit': 'sum'})

# Select only Profit column to match target schema
df_result = df_grouped[['Profit']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)