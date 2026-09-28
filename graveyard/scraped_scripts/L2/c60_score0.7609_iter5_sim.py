import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

joined_1_0 = pd.merge(src1, src0, on="Cust_id", how="inner")
joined_all = pd.merge(joined_1_0, src2, on="Prod_id", how="inner")

agg = joined_all.groupby(
    ["Province", "Region", "Customer_Segment", "Prod_id", "Cust_id", "Product_Category"],
    as_index=False
).agg({
    "Sales": "sum",
    "Order_Quantity": "sum",
    "Profit": "sum",
    "Shipping_Cost": "sum"
})

agg = pd.merge(agg, joined_all[[
    "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Discount", "Product_Base_Margin", "Product_Sub_Category", "Customer_Name"
]].drop_duplicates(subset=["Ord_id"]), on=["Prod_id", "Cust_id"], how="left")

agg = agg[[
    "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount", "Order_Quantity", "Profit", "Shipping_Cost",
    "Product_Base_Margin", "Product_Category", "Product_Sub_Category", "Customer_Name", "Province", "Region", "Customer_Segment"
]]

agg["Order_Quantity"] = agg["Order_Quantity"].astype("Int64")

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)