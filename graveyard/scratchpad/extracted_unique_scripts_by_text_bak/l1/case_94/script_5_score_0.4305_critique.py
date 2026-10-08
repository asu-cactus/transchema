import pandas as pd
import numpy as np

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Add missing columns to df0 to match target schema
df0 = df0.assign(ID=np.nan, shop_id=np.nan, item_id=np.nan)

# Add missing columns to df1 to match target schema
df1 = df1.assign(Store=np.nan, Dept=np.nan, Date=np.nan, Weekly_Sales=np.nan, IsHoliday=np.nan)

# Reorder columns to match target schema exactly
target_columns = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']
df0 = df0[target_columns]
df1 = df1[target_columns]

# Union the two dataframes vertically
merged = pd.concat([df0, df1], ignore_index=True)

# Convert types to match target schema
merged["Store"] = pd.to_numeric(merged["Store"], errors='coerce')
merged["Dept"] = pd.to_numeric(merged["Dept"], errors='coerce')
merged["Weekly_Sales"] = pd.to_numeric(merged["Weekly_Sales"], errors='coerce')
merged["ID"] = pd.to_numeric(merged["ID"], errors='coerce')
merged["shop_id"] = pd.to_numeric(merged["shop_id"], errors='coerce')
merged["item_id"] = pd.to_numeric(merged["item_id"], errors='coerce')
merged["Date"] = merged["Date"].astype(str)
merged["IsHoliday"] = merged["IsHoliday"].astype(str)

# Write output
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)