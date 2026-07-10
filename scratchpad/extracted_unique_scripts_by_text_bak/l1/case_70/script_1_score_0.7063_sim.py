import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how="inner", on="order_id")

result = merged[[
    "order_id",
    "order_status",
    "order_approved_at",
    "product_id",
    "seller_id",
    "price",
    "freight_value"
]]

result["order_id"] = result["order_id"].astype(str)
result["order_status"] = result["order_status"].astype(str)
result["order_approved_at"] = result["order_approved_at"].astype(str)
result["product_id"] = result["product_id"].astype(str)
result["seller_id"] = result["seller_id"].astype(str)
result["price"] = result["price"].astype(float)
result["freight_value"] = result["freight_value"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_70/target_multisource_mcts.csv", index=False)