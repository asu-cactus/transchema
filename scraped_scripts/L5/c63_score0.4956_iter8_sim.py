import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

agg = s4.groupby("Prod_id").agg(
    Ord_id_count=("Ord_id", "count"),
    Sales_sum=("Sales", "sum"),
    Discount_sum=("Discount", "sum")
).reset_index()

merged = pd.merge(agg, s4, on="Prod_id", how="inner")

result = merged[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales_sum", "Discount_sum"]].copy()
result.rename(columns={"Sales_sum": "Sales", "Discount_sum": "Discount"}, inplace=True)

result["Ord_id"] = result["Ord_id"].apply(lambda x: int(x.split("_")[-1]) if isinstance(x, str) and x.startswith("Ord_") else pd.NA)
result["Ship_id"] = result["Ship_id"].apply(lambda x: int(x.split("_")[-1]) if isinstance(x, str) and x.startswith("SHP_") else pd.NA)
result["Cust_id"] = result["Cust_id"].apply(lambda x: int(x.split("_")[-1]) if isinstance(x, str) and x.startswith("Cust_") else pd.NA)

result["Sales"] = result["Sales"].round().astype("Int64")
result["Discount"] = result["Discount"].round().astype("Int64")

result = result[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)