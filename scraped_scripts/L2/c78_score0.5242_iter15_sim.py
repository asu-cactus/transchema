import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

grouped = src0.groupby(['Prod_id', 'Cust_id']).agg({
    'Shipping_Cost': 'sum',
    'Discount': 'sum',
    'Order_Quantity': 'sum',
    'Sales': 'sum',
    'Profit': 'sum',
    'Product_Base_Margin': 'sum'
}).reset_index()

joined_1 = pd.merge(grouped, src1, on='Prod_id', how='left')
joined_2 = pd.merge(joined_1, src2, on='Cust_id', how='left')

joined_2['Order_Quantity'] = joined_2['Order_Quantity'].astype('Int64')

joined_2 = joined_2.rename(columns={
    'Shipping_Cost': 'Shipping_Cost',
    'Discount': 'Discount',
    'Order_Quantity': 'Order_Quantity',
    'Sales': 'Sales',
    'Profit': 'Profit',
    'Product_Base_Margin': 'Product_Base_Margin',
    'Product_Category': 'Product_Category',
    'Product_Sub_Category': 'Product_Sub_Category',
    'Customer_Name': 'Customer_Name',
    'Province': 'Province',
    'Region': 'Region',
    'Customer_Segment': 'Customer_Segment'
})

joined_2['Ord_id'] = None
joined_2['Ship_id'] = None

final_cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']

final_df = joined_2[final_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)