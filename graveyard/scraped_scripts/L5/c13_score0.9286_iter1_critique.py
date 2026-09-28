import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

# Join source1 and source3 on Prod_id to get Product_Sub_Category
df = pd.merge(source1, source3[['Prod_id', 'Product_Sub_Category']], how='inner', on='Prod_id')

# Join with source4 on Ship_id
df = pd.merge(df, source4[['Ship_id']], how='inner', on='Ship_id')

# Join with source2 on Cust_id
df = pd.merge(df, source2[['Cust_id']], how='inner', on='Cust_id')

# Join with source0 on Ord_id to use all sources
df = pd.merge(df, source0[['Ord_id']], how='inner', on='Ord_id')

# Group by Product_Sub_Category and aggregate
df_grouped = df.groupby('Product_Sub_Category').agg(
    Ord_id=('Ord_id', 'nunique'),
    Prod_id=('Prod_id', 'nunique'),
    Ship_id=('Ship_id', 'nunique'),
    Cust_id=('Cust_id', 'nunique'),
    Sales=('Sales', 'sum'),
    Discount=('Discount', 'sum')
).reset_index()

# Convert all columns to int as per target schema
df_grouped['Ord_id'] = df_grouped['Ord_id'].astype(int)
df_grouped['Prod_id'] = df_grouped['Prod_id'].astype(int)
df_grouped['Ship_id'] = df_grouped['Ship_id'].astype(int)
df_grouped['Cust_id'] = df_grouped['Cust_id'].astype(int)
df_grouped['Sales'] = df_grouped['Sales'].round().astype(int)
df_grouped['Discount'] = df_grouped['Discount'].round().astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)