import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

join_01 = pd.merge(source1, source0, on="Cust_id", how="inner")
join_012 = pd.merge(join_01, source2, on="Prod_id", how="inner")

result = join_012[[
    'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost',
    'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment'
]]

result['Ord_id'] = result['Ord_id'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(str)
result['Ship_id'] = result['Ship_id'].astype(str)
result['Cust_id'] = result['Cust_id'].astype(str)
result['Sales'] = result['Sales'].astype(float)
result['Discount'] = result['Discount'].astype(float)
result['Order_Quantity'] = result['Order_Quantity'].astype(int)
result['Profit'] = result['Profit'].astype(float)
result['Shipping_Cost'] = result['Shipping_Cost'].astype(float)
result['Product_Base_Margin'] = result['Product_Base_Margin'].astype(float)
result['Product_Category'] = result['Product_Category'].astype(str)
result['Product_Sub_Category'] = result['Product_Sub_Category'].astype(str)
result['Customer_Name'] = result['Customer_Name'].astype(str)
result['Province'] = result['Province'].astype(str)
result['Region'] = result['Region'].astype(str)
result['Customer_Segment'] = result['Customer_Segment'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)