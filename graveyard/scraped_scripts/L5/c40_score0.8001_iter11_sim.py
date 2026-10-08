import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

agg = s1.groupby("Ship_id").agg({
    "Order_Quantity": "sum",
    "Shipping_Cost": "sum",
    "Discount": "mean"
}).reset_index()

joined_1 = pd.merge(agg, s1, on="Ship_id", how="inner", suffixes=('_agg', ''))
joined_2 = pd.merge(joined_1, s0, on="Cust_id", how="inner")
joined_3 = pd.merge(joined_2, s2, on="Ord_id", how="inner")
joined_4 = pd.merge(joined_3, s3, on="Prod_id", how="inner")
joined_5 = pd.merge(joined_4, s4, on="Ship_id", how="inner")

result = joined_5[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)