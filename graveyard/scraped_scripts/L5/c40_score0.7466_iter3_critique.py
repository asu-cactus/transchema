import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join Source1 and Source0 on Cust_id
df = pd.merge(source1, source0, on="Cust_id", how="inner")

# Join with Source2 on Ord_id
df = pd.merge(df, source2, on="Ord_id", how="inner")

# Join with Source3 on Prod_id
df = pd.merge(df, source3, on="Prod_id", how="inner")

# Join with Source4 on Ship_id
df = pd.merge(df, source4, on="Ship_id", how="inner")

# Convert IDs to integers after removing prefixes
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Group by Ship_id, Customer_Name, Ord_id and aggregate Prod_id and Cust_id by min
result = df.groupby(["Ship_id", "Customer_Name", "Ord_id"], as_index=False).agg({
    "Prod_id": "min",
    "Cust_id": "min"
})

# Reorder columns to match target schema exactly
result = result[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)