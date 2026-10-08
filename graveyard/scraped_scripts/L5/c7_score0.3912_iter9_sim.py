import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join src4 with src0 to get Product_Sub_Category for each Prod_id
df = src4.merge(src0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='left')

# Group by Product_Sub_Category and aggregate as required
agg = df.groupby('Product_Sub_Category').agg(
    Order_Quantity=('Order_Quantity', 'sum'),
    Ord_id=('Ord_id', 'count'),
    Prod_id=('Prod_id', pd.Series.nunique),
    Ship_id=('Ship_id', pd.Series.nunique),
    Cust_id=('Cust_id', pd.Series.nunique),
    Sales=('Sales', 'sum'),
    Discount=('Discount', 'mean')
).reset_index()

# Convert columns to target types
agg['Order_Quantity'] = agg['Order_Quantity'].astype(int)
agg['Ord_id'] = agg['Ord_id'].astype(int)
agg['Prod_id'] = agg['Prod_id'].astype(int)
agg['Ship_id'] = agg['Ship_id'].astype(int)
agg['Cust_id'] = agg['Cust_id'].astype(int)
agg['Sales'] = agg['Sales'].round().astype(int)
agg['Discount'] = agg['Discount'].round().astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)