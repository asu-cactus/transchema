import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

pivot_result = source0.pivot_table(index='Ord_id', 
                                   values=['Order_Date', 'Order_Priority'], 
                                   aggfunc='first').reset_index()

join_result_1 = pd.merge(pivot_result, source3, how='inner', left_on='Ord_id', right_on='Prod_id', suffixes=('', '_drop'))
if 'Prod_id_drop' in join_result_1.columns:
    join_result_1 = join_result_1.drop(columns=['Prod_id_drop'])

# The above join is incorrect because source0 has Ord_id, source3 has Prod_id, no direct join on these.
# Reconsider plan: The partial plan says PIVOT first, but pivoting source0 on Ord_id with Order_Date and Order_Priority is not useful for target.
# The target needs Product_Sub_Category, Ord_id, Prod_id, Ship_id, Cust_id, Sales, Discount.
# source3 has Product_Sub_Category and Prod_id
# source1 has Ord_id, Prod_id, Ship_id, Cust_id, Sales, Discount
# source4 has Ship_id
# source2 has Cust_id
# source0 has Ord_id but only Order_Date and Order_Priority, no direct use for target columns.

# So better to join source1 with source3 on Prod_id to get Product_Sub_Category
# Then join with source4 on Ship_id
# Then join with source2 on Cust_id
# source0 is not needed for target columns.

# Rebuild plan accordingly:

# Join source1 and source3 on Prod_id
df = pd.merge(source1, source3[['Prod_id', 'Product_Sub_Category']], how='inner', on='Prod_id')

# Join with source4 on Ship_id
df = pd.merge(df, source4[['Ship_id']], how='inner', on='Ship_id')

# Join with source2 on Cust_id
df = pd.merge(df, source2[['Cust_id']], how='inner', on='Cust_id')

# Select and convert columns to target schema and types
df_target = df[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

# Convert Sales and Discount to integer by rounding
df_target['Sales'] = df_target['Sales'].round().astype(int)
df_target['Discount'] = df_target['Discount'].round().astype(int)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)