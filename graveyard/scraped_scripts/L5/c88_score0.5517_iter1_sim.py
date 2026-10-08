import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

# UNPIVOT df2 on specified columns
value_vars = ['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin']
unpivot = df2.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=value_vars, var_name='Measure', value_name='Value')

# Filter only Profit rows since target schema only has Profit
profit_df = unpivot[unpivot['Measure'] == 'Profit'].copy()

# Join with df0 on Prod_id
join_0 = profit_df.merge(df0, on='Prod_id', how='left')

# Join with df1 on Ship_id
join_1 = join_0.merge(df1, left_on='Ship_id', right_on='Ship_id', how='left')

# Join with df3 on Ord_id
join_2 = join_1.merge(df3, left_on='Ord_id', right_on='Ord_id', how='left')

# Join with df4 on Cust_id
join_3 = join_2.merge(df4, left_on='Cust_id', right_on='Cust_id', how='left')

# Project only Profit column (Value column renamed to Profit)
result = join_3[['Value']].rename(columns={'Value': 'Profit'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv")