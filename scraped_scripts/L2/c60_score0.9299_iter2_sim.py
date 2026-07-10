import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

join_1 = pd.merge(source1, source2, on="Prod_id", how="inner")
join_2 = pd.merge(join_1, source0, on="Cust_id", how="inner")

target_columns = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 
                  'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 
                  'Customer_Name', 'Province', 'Region', 'Customer_Segment']

result = join_2[target_columns]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)