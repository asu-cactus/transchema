import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)  # Ship_Mode, Ship_Date, Ship_id
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)  # Ord_id, Prod_id, Ship_id, Cust_id, Sales, ...
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)  # Order_Date, Order_Priority, Ord_id
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)  # Customer_Name, Province, Region, Customer_Segment, Cust_id
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)  # Product_Category, Product_Sub_Category, Prod_id

# Join Source1 and Source2 on Ord_id
df_join_0 = pd.merge(df1, df2, on="Ord_id", how="inner")

# Join with Source4 on Prod_id
df_join_1 = pd.merge(df_join_0, df4, on="Prod_id", how="inner")

# Join with Source0 on Ship_id
df_join_2 = pd.merge(df_join_1, df0, on="Ship_id", how="inner")

# Join with Source3 on Cust_id
df_join_3 = pd.merge(df_join_2, df3, on="Cust_id", how="inner")

# Select relevant columns
df_selected = df_join_3[["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

# Convert string IDs to integers by removing prefixes
df_selected["Ord_id"] = df_selected["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df_selected["Prod_id"] = df_selected["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df_selected["Ship_id"] = df_selected["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
df_selected["Cust_id"] = df_selected["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Group by all key columns and sum Sales
result = df_selected.groupby(
    ["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False,
).agg({"Sales": "sum"})

# Round Sales and convert to int
result["Sales"] = result["Sales"].round().astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)