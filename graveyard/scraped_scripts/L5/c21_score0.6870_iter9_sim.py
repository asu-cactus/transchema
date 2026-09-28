import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

# PIVOT and GROUP_BY hint: The partial plan suggests pivoting and grouping by Ship_id.
# However, the target schema does not require pivoting columns, but rather joining all sources on keys.

# Start from s4 (Order_Priority, Ord_id) and join with s2 (which has Ship_id, Cust_id, Prod_id, Sales, Discount, Ord_id)
df = pd.merge(s4, s2, on='Ord_id', how='inner')

# Join with s0 on Cust_id to bring customer info (not needed in final output but required to use all sources)
df = pd.merge(df, s0[['Cust_id']], on='Cust_id', how='inner')

# Join with s1 on Prod_id to bring product info (not needed in final output but required to use all sources)
df = pd.merge(df, s1[['Prod_id']], on='Prod_id', how='inner')

# Join with s3 on Ship_id to bring shipping info (not needed in final output but required to use all sources)
df = pd.merge(df, s3[['Ship_id']], on='Ship_id', how='inner')

# Select and convert columns to target schema and types
df_out = df[['Ship_id', 'Order_Priority', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales', 'Discount']].copy()

# Convert types
df_out['Ship_id'] = df_out['Ship_id'].astype(str)
df_out['Order_Priority'] = df_out['Order_Priority'].astype(str)
df_out['Ord_id'] = df_out['Ord_id'].str.replace('Ord_', '').astype(int)
df_out['Prod_id'] = df_out['Prod_id'].str.replace('Prod_', '').astype(int)
df_out['Cust_id'] = df_out['Cust_id'].str.replace('Cust_', '').astype(int)
df_out['Sales'] = df_out['Sales'].round().astype(int)
df_out['Discount'] = (df_out['Discount'] * 100).round().astype(int)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)