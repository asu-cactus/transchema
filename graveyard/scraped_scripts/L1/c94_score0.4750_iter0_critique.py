import pandas as pd
import numpy as np

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Add missing columns to df0 to match target schema
df0['ID'] = np.nan
df0['shop_id'] = np.nan
df0['item_id'] = np.nan

# Add missing columns to df1 to match target schema
df1['Store'] = np.nan
df1['Dept'] = np.nan
df1['Date'] = np.nan
df1['Weekly_Sales'] = np.nan
df1['IsHoliday'] = np.nan

# Reorder columns to match target schema
target_cols = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']

df0 = df0[target_cols]
df1 = df1[target_cols]

# Convert types to match target schema
df0['Store'] = df0['Store'].astype(float)
df0['Dept'] = df0['Dept'].astype(float)
df0['Weekly_Sales'] = df0['Weekly_Sales'].astype(float)
df0['ID'] = df0['ID'].astype(float)
df0['shop_id'] = df0['shop_id'].astype(float)
df0['item_id'] = df0['item_id'].astype(float)
df0['Date'] = df0['Date'].astype(str)
df0['IsHoliday'] = df0['IsHoliday'].astype(str)

df1['Store'] = df1['Store'].astype(float)
df1['Dept'] = df1['Dept'].astype(float)
df1['Weekly_Sales'] = df1['Weekly_Sales'].astype(float)
df1['ID'] = df1['ID'].astype(float)
df1['shop_id'] = df1['shop_id'].astype(float)
df1['item_id'] = df1['item_id'].astype(float)
df1['Date'] = df1['Date'].astype(str)
df1['IsHoliday'] = df1['IsHoliday'].astype(str)

# Union the two dataframes
result = pd.concat([df0, df1], ignore_index=True)

# Write to output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)