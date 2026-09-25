import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

j0 = pd.merge(s1, s0, on="Ord_id")
j1 = pd.merge(j0, s3, on="Prod_id")
j2 = pd.merge(j1, s4, on="Ship_id")
j3 = pd.merge(j2, s2, on="Cust_id")

agg = j3.groupby(
    ["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False,
).agg({"Sales": "sum", "Discount": "sum"})

agg["Ord_id"] = agg["Ord_id"].str.extract(r"(\d+)").astype(int)
agg["Prod_id"] = agg["Prod_id"].str.extract(r"(\d+)").astype(int)
agg["Ship_id"] = agg["Ship_id"].str.extract(r"(\d+)").astype(int)
agg["Cust_id"] = agg["Cust_id"].str.extract(r"(\d+)").astype(int)
agg["Sales"] = agg["Sales"].round().astype(int)
agg["Discount"] = agg["Discount"].round().astype(int)

agg = agg[
    [
        "Product_Sub_Category",
        "Ord_id",
        "Prod_id",
        "Ship_id",
        "Cust_id",
        "Sales",
        "Discount",
    ]
]

agg.to_csv(
    "autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv",
    index=False,
)