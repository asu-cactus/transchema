import pandas as pd
import numpy as np

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Target schema columns
target_cols = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']

# Add missing columns to df0 with NaN
for col in ['ID', 'shop_id', 'item_id']:
    df0[col] = np.nan

# Add missing columns to df1 with NaN
for col in ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday']:
    df1[col] = np.nan

# Reorder columns to match target schema
df0 = df0[target_cols]
df1 = df1[target_cols]

# Cast columns to target types
df0 = df0.astype({
    'Store': float,
    'Dept': float,
    'Date': str,
    'Weekly_Sales': float,
    'IsHoliday': str,
    'ID': float,
    'shop_id': float,
    'item_id': float
})

df1 = df1.astype({
    'Store': float,
    'Dept': float,
    'Date': str,
    'Weekly_Sales': float,
    'IsHoliday': str,
    'ID': float,
    'shop_id': float,
    'item_id': float
})

# Union the two dataframes (concatenate)
result = pd.concat([df0, df1], ignore_index=True)

# Write to output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)