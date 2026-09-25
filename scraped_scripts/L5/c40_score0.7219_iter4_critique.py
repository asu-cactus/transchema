import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join Source1 and Source4 on Ship_id
join_1_4 = pd.merge(source1, source4, on="Ship_id")

# Join with Source0 on Cust_id
join_1_4_0 = pd.merge(join_1_4, source0, on="Cust_id")

# Join with Source2 on Ord_id
join_1_4_0_2 = pd.merge(join_1_4_0, source2, on="Ord_id")

# Join with Source3 on Prod_id
join_all = pd.merge(join_1_4_0_2, source3, on="Prod_id")

# Select required columns
result = join_all[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]]

# Convert Ord_id, Prod_id, Cust_id to integer by extracting numeric suffix
result["Ord_id"] = result["Ord_id"].str.extract(r"(\d+)").astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r"(\d+)").astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r"(\d+)").astype(int)

# Group by all columns to remove duplicates if any
result = result.groupby(["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"], as_index=False).size()
result = result.drop(columns="size")  # size is just to trigger groupby, drop it

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)