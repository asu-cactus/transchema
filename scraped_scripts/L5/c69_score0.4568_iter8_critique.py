import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

join_result_1 = pd.merge(source3, source2, on="Cust_id", how="inner")
join_result_2 = pd.merge(join_result_1, source4, on="Ship_id", how="inner")
join_result_3 = pd.merge(join_result_2, source1, on="Ord_id", how="inner")

# Select relevant columns
df = join_result_3[["Ship_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]].copy()

# Convert columns to target types
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)
df["Ship_Date"] = df["Ship_Date"].astype(str)

# Group by all target columns to remove duplicates, count Ord_id just to aggregate
df_grouped = df.groupby(["Ship_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"], as_index=False).agg({"Ord_id": "count"})

# Drop the aggregation column to match target schema exactly
df_final = df_grouped.drop(columns=["Ord_id"])

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)