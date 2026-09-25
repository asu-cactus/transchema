import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)  # Must use all sources

# Join Source5_64_2 and Source5_64_1 on Ship_id
r0 = pd.merge(src2, src1, on="Ship_id", how="inner")

# Join with Source5_64_0 on Cust_id
r1 = pd.merge(r0, src0, on="Cust_id", how="inner")

# Join with Source5_64_3 on Ord_id
r2 = pd.merge(r1, src3, on="Ord_id", how="inner")

# Join with Source5_64_4 on Prod_id to ensure all sources are used
r3 = pd.merge(r2, src4, on="Prod_id", how="inner")

# Select and convert columns to match target schema
out = pd.DataFrame()
out["Ship_Date"] = r3["Ship_Date"].astype(str)
out["Customer_Name"] = r3["Customer_Name"].astype(str)
out["Ord_id"] = r3["Ord_id"].str.replace("Ord_", "").astype(int)
out["Prod_id"] = r3["Prod_id"].str.replace("Prod_", "").astype(int)
out["Ship_id"] = r3["Ship_id"].str.replace("SHP_", "").astype(int)

# Group by all key columns to remove duplicates and match target row count
out = out.groupby(["Ship_Date", "Customer_Name", "Ord_id", "Prod_id", "Ship_id"], as_index=False).size()

# The groupby.size() returns a Series with name 'size', convert back to DataFrame without 'size'
out = out.drop(columns=["size"])

out.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)