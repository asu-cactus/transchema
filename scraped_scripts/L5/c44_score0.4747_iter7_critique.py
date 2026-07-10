import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)  # Order_Date, Order_Priority, Ord_id
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)  # Customer_Name, Province, Region, Customer_Segment, Cust_id
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)  # Product_Category, Product_Sub_Category, Prod_id
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)  # Ship_Mode, Ship_Date, Ship_id
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)  # Ord_id, Prod_id, Ship_id, Cust_id, Sales, ...

# Join Source5_44_4 with Source5_44_0 on Ord_id
df = s4.merge(s0[['Ord_id']], on='Ord_id', how='inner')

# Join with Source5_44_1 on Cust_id
df = df.merge(s1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='inner')

# Join with Source5_44_2 on Prod_id
df = df.merge(s2[['Prod_id']], on='Prod_id', how='inner')

# Join with Source5_44_3 on Ship_id
df = df.merge(s3[['Ship_id']], on='Ship_id', how='inner')

# Extract numeric part from IDs to convert to integer
df['Ord_id'] = df['Ord_id'].str.extract(r'(\d+)').astype(int)
df['Prod_id'] = df['Prod_id'].str.extract(r'(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract(r'(\d+)').astype(int)
df['Cust_id'] = df['Cust_id'].str.extract(r'(\d+)').astype(int)

# Select columns in target schema order
df_out = df[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

# Write output
df_out.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)