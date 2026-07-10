import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

join_4_1 = pd.merge(source4, source1, on="Cust_id", how="inner")
join_4_1_0 = pd.merge(join_4_1, source0, on="Prod_id", how="inner")
join_4_1_0_2 = pd.merge(join_4_1_0, source2, on="Ord_id", how="inner")
final_join = pd.merge(join_4_1_0_2, source3, on="Ship_id", how="inner")

result = final_join[[
    "Product_Sub_Category",
    "Order_Quantity",
    "Ord_id",
    "Prod_id",
    "Ship_id",
    "Cust_id",
    "Sales",
    "Discount"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)