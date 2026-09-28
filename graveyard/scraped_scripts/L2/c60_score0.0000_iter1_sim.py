import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True, sort=False)

merged = pd.merge(source1, union_result, how='inner', on=['Prod_id', 'Cust_id'])

merged = merged[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']]

merged = merged.astype({
    'Ord_id': str,
    'Prod_id': str,
    'Ship_id': str,
    'Cust_id': str,
    'Sales': float,
    'Discount': float,
    'Order_Quantity': int,
    'Profit': float,
    'Shipping_Cost': float,
    'Product_Base_Margin': float,
    'Product_Category': str,
    'Product_Sub_Category': str,
    'Customer_Name': str,
    'Province': str,
    'Region': str,
    'Customer_Segment': str
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)