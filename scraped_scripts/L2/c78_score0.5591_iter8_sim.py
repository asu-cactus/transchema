import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], axis=0, ignore_index=True, sort=False)

merged = pd.merge(source0, union_result, how='left', left_on=['Prod_id', 'Cust_id'], right_on=['Prod_id', 'Cust_id'])

cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin',
        'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']

result = merged[cols]

result['Order_Quantity'] = result['Order_Quantity'].astype('Int64')
result['Sales'] = result['Sales'].astype(float)
result['Discount'] = result['Discount'].astype(float)
result['Profit'] = result['Profit'].astype(float)
result['Shipping_Cost'] = result['Shipping_Cost'].astype(float)
result['Product_Base_Margin'] = pd.to_numeric(result['Product_Base_Margin'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)