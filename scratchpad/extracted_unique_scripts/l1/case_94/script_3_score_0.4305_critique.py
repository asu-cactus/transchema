import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Add missing columns to df0
df0["ID"] = np.nan
df0["shop_id"] = np.nan
df0["item_id"] = np.nan

# Add missing columns to df1
df1["Store"] = np.nan
df1["Dept"] = np.nan
df1["Date"] = np.nan
df1["Weekly_Sales"] = np.nan
df1["IsHoliday"] = np.nan

# Reorder columns to match target schema
target_columns = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']

df0 = df0[target_columns]
df1 = df1[target_columns]

# Concatenate (UNION)
result = pd.concat([df0, df1], ignore_index=True)

# Cast columns to target types
result["Store"] = result["Store"].astype(float)
result["Dept"] = result["Dept"].astype(float)
result["Date"] = result["Date"].astype(str)
result["Weekly_Sales"] = result["Weekly_Sales"].astype(float)
result["IsHoliday"] = result["IsHoliday"].astype(str)
result["ID"] = result["ID"].astype(float)
result["shop_id"] = result["shop_id"].astype(float)
result["item_id"] = result["item_id"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)