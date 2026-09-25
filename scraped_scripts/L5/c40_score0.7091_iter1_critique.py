import pandas as pd

# Read all source files with index_col=0 to ignore the first index column
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join Source1 with Source0 on Cust_id
df = pd.merge(src1, src0[['Customer_Name', 'Cust_id']], how='inner', on='Cust_id')

# Join with Source2 on Ord_id
df = pd.merge(df, src2[['Ord_id']], how='inner', on='Ord_id')

# Join with Source3 on Prod_id
df = pd.merge(df, src3[['Prod_id']], how='inner', on='Prod_id')

# Join with Source4 on Ship_id
df = pd.merge(df, src4[['Ship_id']], how='inner', on='Ship_id')

# Convert Ord_id, Prod_id, Cust_id from strings like 'Ord_1082' to integers
df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df['Prod_id'] = df['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
df['Cust_id'] = df['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Select only the target columns in the correct order
result = df[['Ship_id', 'Customer_Name', 'Ord_id', 'Prod_id', 'Cust_id']]

# Remove duplicates by grouping by all columns (no aggregation needed)
result = result.drop_duplicates()

# Write to output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)