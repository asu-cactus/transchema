import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)

s0_renamed = s0.rename(columns={"Order_Date": "Order_Date", "Ord_id": "Ord_id"})
s4_renamed = s4.rename(columns={"Ord_id": "Ord_id", "Prod_id": "Prod_id", "Ship_id": "Ship_id", "Cust_id": "Cust_id", "Sales": "Sales", "Discount": "Discount"})

# For union, columns must match exactly. s0 has ['Order_Date', 'Order_Priority', 'Ord_id'], s4 has many columns.
# We keep only columns in target schema from s0 and s4, filling missing columns with NaN or appropriate default.

# Prepare s0 for union: keep Order_Date and Ord_id, add missing columns with NaN
s0_sub = s0[["Order_Date", "Ord_id"]].copy()
s0_sub["Prod_id"] = pd.NA
s0_sub["Ship_id"] = pd.NA
s0_sub["Cust_id"] = pd.NA
s0_sub["Sales"] = pd.NA
s0_sub["Discount"] = pd.NA

# Prepare s4 for union: keep only target columns
s4_sub = s4[["Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()
# s4 has no Order_Date, add it as NaN
s4_sub["Order_Date"] = pd.NA
# reorder columns to match s0_sub
s4_sub = s4_sub[["Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

union_df = pd.concat([s0_sub, s4_sub], ignore_index=True)

# Join union_df with s1 on Ship_id
join1 = pd.merge(union_df, s1[["Ship_id"]], on="Ship_id", how="left", suffixes=("", "_s1"))

# Join join1 with s2 on Cust_id
join2 = pd.merge(join1, s2[["Cust_id"]], on="Cust_id", how="left", suffixes=("", "_s2"))

# Join join2 with s3 on Prod_id
join3 = pd.merge(join2, s3[["Prod_id"]], on="Prod_id", how="left", suffixes=("", "_s3"))

# Now fix data types and fill missing values where appropriate
# Order_Date: string, keep as is (some NaN from s4)
# Ord_id, Prod_id, Ship_id, Cust_id: string IDs, keep as is
# Sales, Discount: convert to numeric (float), then to integer if possible, else keep float
# But target schema says integer for Sales and Discount, so convert with rounding or floor

join3["Sales"] = pd.to_numeric(join3["Sales"], errors="coerce")
join3["Discount"] = pd.to_numeric(join3["Discount"], errors="coerce")

# Convert Sales and Discount to integer, keep NaN if any
join3["Sales"] = join3["Sales"].dropna().astype(int)
join3["Discount"] = join3["Discount"].dropna().astype(int)

# Final projection and reorder columns
final_df = join3[["Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)