import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join Source1 and Source4 on Ship_id
join_1_4 = pd.merge(source1, source4, how="inner", on="Ship_id")

# Join the above with Source2 on Ord_id
join_1_4_2 = pd.merge(join_1_4, source2, how="inner", on="Ord_id")

# Join the above with Source3 on Prod_id
join_all = pd.merge(join_1_4_2, source3, how="inner", on="Prod_id")

# Join the above with Source0 on Cust_id
final_join = pd.merge(join_all, source0, how="inner", on="Cust_id")

# Select and rename columns to match target schema
result = final_join[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]].copy()

# Remove prefixes and convert to int for Ord_id, Prod_id, Cust_id
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Write to output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)