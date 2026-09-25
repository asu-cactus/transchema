import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

# Join Source4 with Source2 on Ship_id
result = pd.merge(df4, df2, on="Ship_id", how="inner")
# Join with Source0 on Ord_id
result = pd.merge(result, df0, on="Ord_id", how="inner")
# Join with Source1 on Cust_id
result = pd.merge(result, df1, on="Cust_id", how="inner")
# Join with Source3 on Prod_id
result = pd.merge(result, df3, on="Prod_id", how="inner")

# Group by Ship_Mode and aggregate counts of distinct IDs and sum of Sales
grouped = result.groupby("Ship_Mode").agg({
    "Ord_id": pd.Series.nunique,
    "Prod_id": pd.Series.nunique,
    "Ship_id": pd.Series.nunique,
    "Cust_id": pd.Series.nunique,
    "Sales": "sum"
}).reset_index()

# Convert all aggregated columns to int as per target schema
grouped["Ord_id"] = grouped["Ord_id"].astype(int)
grouped["Prod_id"] = grouped["Prod_id"].astype(int)
grouped["Ship_id"] = grouped["Ship_id"].astype(int)
grouped["Cust_id"] = grouped["Cust_id"].astype(int)
grouped["Sales"] = grouped["Sales"].round().astype(int)

# Reorder columns to match target schema
grouped = grouped[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)