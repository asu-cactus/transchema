import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

source0_cols = set(source0.columns)
source1_cols = set(source1.columns)

common_cols = list(source0_cols.intersection(source1_cols))
union_result = pd.concat([source0[common_cols], source1[common_cols]], ignore_index=True)

join_result_1 = pd.merge(source1, source2, on="Prod_id", how="left")
final_result = pd.merge(join_result_1, source0, on="Cust_id", how="left")

final_result = final_result[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)