import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

join_0_2 = pd.merge(source0, source2, how='inner', on='Cust_id')
final = pd.merge(join_0_2, source1, how='inner', on='Prod_id')

final = final[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']]

final['Ord_id'] = final['Ord_id'].astype(str)
final['Prod_id'] = final['Prod_id'].astype(str)
final['Ship_id'] = final['Ship_id'].astype(str)
final['Cust_id'] = final['Cust_id'].astype(str)
final['Sales'] = final['Sales'].astype(float)
final['Discount'] = final['Discount'].astype(float)
final['Order_Quantity'] = final['Order_Quantity'].astype(int)
final['Profit'] = final['Profit'].astype(float)
final['Shipping_Cost'] = final['Shipping_Cost'].astype(float)
final['Product_Base_Margin'] = final['Product_Base_Margin'].astype(float)
final['Product_Category'] = final['Product_Category'].astype(str)
final['Product_Sub_Category'] = final['Product_Sub_Category'].astype(str)
final['Customer_Name'] = final['Customer_Name'].astype(str)
final['Province'] = final['Province'].astype(str)
final['Region'] = final['Region'].astype(str)
final['Customer_Segment'] = final['Customer_Segment'].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)