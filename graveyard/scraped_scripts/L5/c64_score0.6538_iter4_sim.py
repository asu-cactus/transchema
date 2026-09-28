import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)

# PIVOT on s1 by Ship_Date grouping Ship_id (pivoting Ship_Mode is not needed, just keep Ship_Date and Ship_id)
# The partial plan says PIVOT and GROUP_BY on Ship_Date, but the target schema only needs Ship_Date and Ship_id (integer).
# Ship_id in s1 is like SHP_1, SHP_2, so we convert Ship_id to integer by removing 'SHP_' prefix.
s1['Ship_id'] = s1['Ship_id'].str.replace('SHP_', '').astype(int)
pivot_result = s1[['Ship_Date', 'Ship_id']].drop_duplicates()

# s2 has Ship_id as SHP_xxxx, convert similarly to int for join
s2['Ship_id'] = s2['Ship_id'].str.replace('SHP_', '').astype(int)

# Join pivot_result with s2 on Ship_id
join_result = pd.merge(pivot_result, s2, on='Ship_id', how='inner')

# s0 has Cust_id like Cust_1, Cust_2; s2 also has Cust_id like Cust_417 etc.
# Join join_result with s0 on Cust_id
join_result = pd.merge(join_result, s0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')

# s3 has Ord_id like Ord_1, Ord_2; s2 has Ord_id like Ord_1082 etc.
# Join join_result with s3 on Ord_id
join_result = pd.merge(join_result, s3[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

# Target schema: ['Ship_Date': string, 'Customer_Name': string, 'Ord_id': integer, 'Prod_id': integer, 'Ship_id': integer]
# Current join_result columns: Ship_Date (string), Customer_Name (string), Ord_id (string like Ord_1082), Prod_id (string like Prod_8), Ship_id (int)
# Convert Ord_id and Prod_id to integer by removing prefix 'Ord_' and 'Prod_'
join_result['Ord_id'] = join_result['Ord_id'].str.replace('Ord_', '').astype(int)
join_result['Prod_id'] = join_result['Prod_id'].str.replace('Prod_', '').astype(int)

# Ship_id is already int, Ship_Date is string, Customer_Name is string

# Select and reorder columns as target schema
target = join_result[['Ship_Date', 'Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)