import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

# Join Source0 and Source2 on Cust_id
join_0_2 = pd.merge(source0, source2, on="Cust_id", how="inner")

# Join the above result with Source1 on Prod_id
join_all = pd.merge(join_0_2, source1, on="Prod_id", how="inner")

# Group by the leftmost key columns
group_cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

agg_dict = {
    'Sales': 'sum',
    'Discount': 'mean',
    'Order_Quantity': 'sum',
    'Profit': 'sum',
    'Shipping_Cost': 'sum',
    'Product_Base_Margin': 'mean',
    'Product_Category': 'first',
    'Product_Sub_Category': 'first',
    'Customer_Name': 'first',
    'Province': 'first',
    'Region': 'first',
    'Customer_Segment': 'first'
}

final_df = join_all.groupby(group_cols, as_index=False).agg(agg_dict)

# Ensure column order matches target schema exactly
final_df = final_df[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']]

# Cast Order_Quantity to Int64 nullable integer type
final_df['Order_Quantity'] = final_df['Order_Quantity'].astype('Int64')

# Cast float columns explicitly
final_df['Sales'] = final_df['Sales'].astype(float)
final_df['Discount'] = final_df['Discount'].astype(float)
final_df['Profit'] = final_df['Profit'].astype(float)
final_df['Shipping_Cost'] = final_df['Shipping_Cost'].astype(float)
final_df['Product_Base_Margin'] = final_df['Product_Base_Margin'].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)