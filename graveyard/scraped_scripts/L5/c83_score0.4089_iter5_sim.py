import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

join_0 = pd.merge(source4, source0, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, source1, left_on="Ord_id", right_on="Ord_id", how="inner")
join_2 = pd.merge(join_1, source2, left_on="Ship_id", right_on="Ship_id", how="inner")
join_3 = pd.merge(join_2, source3, left_on="Prod_id", right_on="Prod_id", how="inner")

grouped = join_3.groupby([
    "Customer_Segment", "Ship_Mode", "Product_Category", "Province", "Region",
    "Order_Date", "Order_Priority", "Ship_Date", "Prod_id", "Cust_id"
], dropna=False).agg({
    "Profit": "sum",
    "Sales": "sum",
    "Order_Quantity": "sum",
    "Shipping_Cost": "sum"
}).reset_index()

result = grouped[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)