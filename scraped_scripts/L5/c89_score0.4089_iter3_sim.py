import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

join_1 = pd.merge(source4, source2, on="Ord_id", how="inner")
join_2 = pd.merge(join_1, source3, on="Ship_id", how="inner")
join_3 = pd.merge(join_2, source1, on="Cust_id", how="inner")
join_4 = pd.merge(join_3, source0, on="Prod_id", how="inner")

grouped = join_4.groupby([
    "Product_Category",
    "Customer_Segment",
    "Ship_Mode",
    "Province",
    "Region",
    "Order_Date",
    "Order_Priority",
    "Ship_Date",
    "Prod_id",
    "Cust_id"
], dropna=False, as_index=False)["Profit"].sum()

result = grouped[["Profit"]].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)