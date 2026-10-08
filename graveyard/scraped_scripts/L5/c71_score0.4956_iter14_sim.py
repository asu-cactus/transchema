import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

df = pd.merge(source0, source4, on="Ord_id", how="inner")
df = pd.merge(df, source1, on="Cust_id", how="inner")
df = pd.merge(df, source3, on="Prod_id", how="inner")
df = pd.merge(df, source2, on="Ship_id", how="inner")

agg = df.groupby(
    ["Ship_Mode", "Order_Priority", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False
).agg({
    "Sales": "min",
    "Discount": "min"
})

agg["Sales"] = agg["Sales"].round().astype("Int64")
agg["Discount"] = agg["Discount"].round().astype("Int64")

result = agg[["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)