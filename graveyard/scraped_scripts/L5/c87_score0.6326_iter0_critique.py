import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

# Join Source5_87_2 and Source5_87_0 on Ship_id
result = pd.merge(df2, df0, how='inner', left_on='Ship_id', right_on='Ship_id')

# Join with Source5_87_4 on Ord_id
result = pd.merge(result, df4, how='inner', left_on='Ord_id', right_on='Ord_id')

# Join with Source5_87_1 on Prod_id
result = pd.merge(result, df1, how='inner', left_on='Prod_id', right_on='Prod_id')

# Join with Source5_87_3 on Cust_id
result = pd.merge(result, df3, how='inner', left_on='Cust_id', right_on='Cust_id')

# Group by Product_Category and Customer_Segment, aggregate sum of Profit
agg = result.groupby(['Product_Category', 'Customer_Segment'], as_index=False)['Profit'].sum()

# Select only the Profit column to match target schema
target = agg[['Profit']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)