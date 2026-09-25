import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

join_0 = pd.merge(source0, source1, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, source3, on="Prod_id", how="inner")
join_2 = pd.merge(join_1, source2, on="Ship_id", how="inner")
join_3 = pd.merge(join_2, source4, on="Ord_id", how="inner")

agg = join_3.groupby(
    ["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False
).agg({
    "Sales": "sum",
    "Discount": "sum"
})

agg["Sales"] = agg["Sales"].round().astype(int)
agg["Discount"] = agg["Discount"].round().astype(int)

agg = agg[["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)