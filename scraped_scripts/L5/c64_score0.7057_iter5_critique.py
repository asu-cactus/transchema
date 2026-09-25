import pandas as pd

# Read source files with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)

# Join df2 and df0 on Cust_id
df_merged_0 = pd.merge(df2, df0, on="Cust_id", how="inner")

# Join with df1 on Ship_id
df_merged_1 = pd.merge(df_merged_0, df1, on="Ship_id", how="inner")

# Join with df3 on Ord_id
df_merged_2 = pd.merge(df_merged_1, df3, on="Ord_id", how="inner")

# Join with df4 on Prod_id
df_merged_3 = pd.merge(df_merged_2, df4, on="Prod_id", how="inner")

# Extract integer parts from Ord_id, Prod_id, Ship_id
df_merged_3["Ord_id"] = df_merged_3["Ord_id"].str.extract(r'(\d+)').astype(int)
df_merged_3["Prod_id"] = df_merged_3["Prod_id"].str.extract(r'(\d+)').astype(int)
df_merged_3["Ship_id"] = df_merged_3["Ship_id"].str.extract(r'(\d+)').astype(int)

# Select target columns
result = df_merged_3[["Ship_Date", "Customer_Name", "Ord_id", "Prod_id", "Ship_id"]]

# Group by all target columns to remove duplicates (no aggregation)
result = result.drop_duplicates()

# Write to CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)