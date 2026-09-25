import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)

df = pd.merge(df2, df0, on="Cust_id", how="inner")
df = pd.merge(df, df1, on="Ship_id", how="inner")
df = pd.merge(df, df3, on="Ord_id", how="inner")
df = pd.merge(df, df4, on="Prod_id", how="inner")

df["Ship_Date"] = df["Ship_Date"].astype(str)
df["Customer_Name"] = df["Customer_Name"].astype(str)
df["Ord_id"] = df["Ord_id"].astype(str).str.replace("Ord_", "").astype(int)
df["Prod_id"] = df["Prod_id"].astype(str).str.replace("Prod_", "").astype(int)
df["Ship_id"] = df["Ship_id"].astype(str).str.replace("SHP_", "").astype(int)

grouped = df.groupby(["Ship_Date", "Customer_Name", "Ord_id"], as_index=False).agg({
    "Prod_id": "min",
    "Ship_id": "min"
})

result = grouped[["Ship_Date", "Customer_Name", "Ord_id", "Prod_id", "Ship_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)