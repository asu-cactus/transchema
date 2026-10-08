import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

df = source4.merge(source0, on="Prod_id", how="inner")
df = df.merge(source1, on="Cust_id", how="inner")
df = df.merge(source2, left_on="Ord_id", right_on="Ord_id", how="inner")
df = df.merge(source3, left_on="Ship_id", right_on="Ship_id", how="inner")

group_cols = [
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
]

agg_df = df.groupby(group_cols).agg(
    Profit_min=pd.NamedAgg(column="Profit", aggfunc="min"),
    Profit_max=pd.NamedAgg(column="Profit", aggfunc="max"),
    Discount_sum=pd.NamedAgg(column="Discount", aggfunc="sum"),
    Shipping_Cost_sum=pd.NamedAgg(column="Shipping_Cost", aggfunc="sum")
).reset_index()

agg_df["Profit"] = agg_df["Profit_max"] - agg_df["Profit_min"] + agg_df["Discount_sum"] + agg_df["Shipping_Cost_sum"]

result = agg_df[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)