import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

union_result = pd.concat([source0, source1], ignore_index=True, sort=False)

joined = union_result.merge(source2, on="Prod_id", how="left")

final_cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 
              'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']

result = joined[final_cols]

result['Ord_id'] = result['Ord_id'].astype('string')
result['Prod_id'] = result['Prod_id'].astype('string')
result['Ship_id'] = result['Ship_id'].astype('string')
result['Cust_id'] = result['Cust_id'].astype('string')
result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce')
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce')
result['Order_Quantity'] = pd.to_numeric(result['Order_Quantity'], errors='coerce').astype('Int64')
result['Profit'] = pd.to_numeric(result['Profit'], errors='coerce')
result['Shipping_Cost'] = pd.to_numeric(result['Shipping_Cost'], errors='coerce')
result['Product_Base_Margin'] = pd.to_numeric(result['Product_Base_Margin'], errors='coerce')
result['Product_Category'] = result['Product_Category'].astype('string')
result['Product_Sub_Category'] = result['Product_Sub_Category'].astype('string')
result['Customer_Name'] = result['Customer_Name'].astype('string')
result['Province'] = result['Province'].astype('string')
result['Region'] = result['Region'].astype('string')
result['Customer_Segment'] = result['Customer_Segment'].astype('string')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)