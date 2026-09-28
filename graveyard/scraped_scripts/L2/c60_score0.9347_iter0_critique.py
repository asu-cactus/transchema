import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

# Join Source1 and Source0 on Cust_id
join_01 = pd.merge(source1, source0, on="Cust_id", how="inner")

# Join the above result with Source2 on Prod_id
join_012 = pd.merge(join_01, source2, on="Prod_id", how="inner")

# Group by the leftmost key columns to remove duplicates and aggregate numeric columns by sum
grouped = join_012.groupby(['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum',
    'Order_Quantity': 'sum',
    'Profit': 'sum',
    'Shipping_Cost': 'sum',
    'Product_Base_Margin': 'sum',
    'Product_Category': 'first',
    'Product_Sub_Category': 'first',
    'Customer_Name': 'first',
    'Province': 'first',
    'Region': 'first',
    'Customer_Segment': 'first'
})

# Ensure correct dtypes as per target schema
grouped['Ord_id'] = grouped['Ord_id'].astype(str)
grouped['Prod_id'] = grouped['Prod_id'].astype(str)
grouped['Ship_id'] = grouped['Ship_id'].astype(str)
grouped['Cust_id'] = grouped['Cust_id'].astype(str)
grouped['Sales'] = grouped['Sales'].astype(float)
grouped['Discount'] = grouped['Discount'].astype(float)
grouped['Order_Quantity'] = grouped['Order_Quantity'].astype(int)
grouped['Profit'] = grouped['Profit'].astype(float)
grouped['Shipping_Cost'] = grouped['Shipping_Cost'].astype(float)
grouped['Product_Base_Margin'] = grouped['Product_Base_Margin'].astype(float)
grouped['Product_Category'] = grouped['Product_Category'].astype(str)
grouped['Product_Sub_Category'] = grouped['Product_Sub_Category'].astype(str)
grouped['Customer_Name'] = grouped['Customer_Name'].astype(str)
grouped['Province'] = grouped['Province'].astype(str)
grouped['Region'] = grouped['Region'].astype(str)
grouped['Customer_Segment'] = grouped['Customer_Segment'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)