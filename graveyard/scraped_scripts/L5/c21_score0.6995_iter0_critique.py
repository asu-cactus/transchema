import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

result_0 = pd.merge(source2, source4, on="Ord_id", how="inner")
result_1 = pd.merge(result_0, source0, on="Cust_id", how="inner")
result_2 = pd.merge(result_1, source1, on="Prod_id", how="inner")
result_3 = pd.merge(result_2, source3, on="Ship_id", how="inner")

df = result_3[["Ship_id", "Order_Priority", "Ord_id", "Prod_id", "Cust_id", "Sales", "Discount"]].copy()

df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)
df["Sales"] = df["Sales"].round().astype(int)
df["Discount"] = (df["Discount"] * 100).round().astype(int)

grouped = df.groupby(
    ["Ship_id", "Order_Priority", "Ord_id", "Prod_id", "Cust_id"],
    as_index=False,
).agg({"Sales": "sum", "Discount": "sum"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)