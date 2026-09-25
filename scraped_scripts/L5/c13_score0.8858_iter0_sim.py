import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

r0 = pd.merge(s1, s3, on="Prod_id", how="inner")
r1 = pd.merge(r0, s4, on="Ship_id", how="inner")
r2 = pd.merge(r1, s2, on="Cust_id", how="inner")
r3 = pd.merge(r2, s0, on="Ord_id", how="inner")

r3["Sales"] = pd.to_numeric(r3["Sales"], errors='coerce').fillna(0).astype(int)
r3["Discount"] = pd.to_numeric(r3["Discount"], errors='coerce').fillna(0).astype(int)

agg = r3.groupby("Product_Sub_Category").agg({
    "Ord_id": "max",
    "Prod_id": "max",
    "Ship_id": "max",
    "Cust_id": "max",
    "Sales": "sum",
    "Discount": "sum"
}).reset_index()

agg["Ord_id"] = agg["Ord_id"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else None)
agg["Prod_id"] = agg["Prod_id"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else None)
agg["Ship_id"] = agg["Ship_id"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else None)
agg["Cust_id"] = agg["Cust_id"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else None)

agg = agg.astype({
    "Ord_id": "Int64",
    "Prod_id": "Int64",
    "Ship_id": "Int64",
    "Cust_id": "Int64",
    "Sales": "Int64",
    "Discount": "Int64"
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)