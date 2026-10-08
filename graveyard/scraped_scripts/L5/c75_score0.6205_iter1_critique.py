import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_4.csv", index_col=0)

# Join df0 and df1 on Prod_id
df = pd.merge(df0, df1, on='Prod_id', how='inner')

# Join with df2 on Ship_id
df = pd.merge(df, df2, on='Ship_id', how='inner')

# Join with df3 on Ord_id
df = pd.merge(df, df3, on='Ord_id', how='inner')

# Join with df4 on Cust_id
df = pd.merge(df, df4, on='Cust_id', how='inner')

# Group by Region and sum Profit
result = df.groupby('Region', as_index=False)['Profit'].sum()

# Rename columns to match target schema (only 'Profit')
# The target schema has only 'Profit' column, so output only that column
# The target has 4 rows, so Region is only used for grouping, not output
# So output only Profit column
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)