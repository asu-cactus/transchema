import pandas as pd
import numpy as np

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Target schema columns
target_cols = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']

# Add missing columns to df0 with NaN and correct types
for col in ['ID', 'shop_id', 'item_id']:
    df0[col] = np.nan

# Add missing columns to df1 with NaN and correct types
for col in ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday']:
    df1[col] = np.nan

# Reorder columns to target schema
df0 = df0[target_cols]
df1 = df1[target_cols]

# Concatenate (UNION) the two dataframes
result = pd.concat([df0, df1], ignore_index=True)

# Ensure types match target schema:
# Store, Dept: float (from examples)
result['Store'] = result['Store'].astype(float)
result['Dept'] = result['Dept'].astype(float)
# Date: string (object)
result['Date'] = result['Date'].astype(str)
# Weekly_Sales: float
result['Weekly_Sales'] = result['Weekly_Sales'].astype(float)
# IsHoliday: string (from examples, but source0 has bool, so convert bool to string)
# The target examples show IsHoliday as False (boolean-like), but schema says string.
# We'll convert boolean False/True to string 'False'/'True' to match target.
result['IsHoliday'] = result['IsHoliday'].astype(str)
# ID, shop_id, item_id: float
result['ID'] = result['ID'].astype(float)
result['shop_id'] = result['shop_id'].astype(float)
result['item_id'] = result['item_id'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)