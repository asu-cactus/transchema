import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

df = pd.merge(source2, source0, left_on="Prod_id", right_on="Prod_id", how="inner")
df = pd.merge(df, source1, left_on="Ship_id", right_on="Ship_id", how="inner")
df = pd.merge(df, source3, left_on="Ord_id", right_on="Ord_id", how="inner")
df = pd.merge(df, source4, left_on="Cust_id", right_on="Cust_id", how="inner")

group_cols = [
    "Product_Category",
    "Ship_Mode",
    "Customer_Segment",
    "Ship_Date",
    "Prod_id",
    "Cust_id",
    "Order_Date",
    "Order_Priority",
    "Province",
    "Region"
]

agg_df = df.groupby(group_cols, dropna=False, as_index=False)["Profit"].sum()

agg_df[["Profit"]].to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)