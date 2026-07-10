import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

df = pd.merge(source1, source0, on="Ship_id", how="inner")
df = pd.merge(df, source2, on="Ord_id", how="inner")
df = pd.merge(df, source3, on="Cust_id", how="inner")
df = pd.merge(df, source4, on="Prod_id", how="inner")

df = df.rename(columns={"Order_Date": "Order_Date", "Product_Sub_Category": "Product_Sub_Category",
                        "Ord_id": "Ord_id", "Prod_id": "Prod_id", "Ship_id": "Ship_id",
                        "Cust_id": "Cust_id", "Sales": "Sales"})

df = df[["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "").astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "").astype(int)
df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "").astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "").astype(int)
df["Order_Date"] = df["Order_Date"].astype(str)
df["Product_Sub_Category"] = df["Product_Sub_Category"].astype(str)
df["Sales"] = pd.to_numeric(df["Sales"], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)