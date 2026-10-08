import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

# Join df2 with df0 on Prod_id
df_20 = pd.merge(df2, df0, how='inner', on='Prod_id')

# Join df2 with df3 on Ord_id
df_203 = pd.merge(df_20, df3, how='inner', on='Ord_id')

# Join df3 with df1 on Order_ID
df_2031 = pd.merge(df_203, df1, how='inner', on='Order_ID')

# Join df2 with df4 on Cust_id
# Note: df_2031 already contains df2, so join df_2031 with df4 on Cust_id
df_all = pd.merge(df_2031, df4, how='inner', on='Cust_id')

# Group by Product_Category and Product_Sub_Category, aggregate sum of Profit
result = df_all.groupby(['Product_Category', 'Product_Sub_Category'], as_index=False)['Profit'].sum()

# Write output with exact target schema ['Profit']
# The target schema is only ['Profit'], so output only that column
# But target examples have 17 tuples, so grouping by these two columns reduces rows to 17
# The target does not have the grouping columns, so drop them before output
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)