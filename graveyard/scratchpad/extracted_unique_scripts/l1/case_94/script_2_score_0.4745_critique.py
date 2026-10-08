import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

# Define target columns
target_cols = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']

# Prepare df0 to match target schema: add missing columns with NaN
df0_expanded = df0.copy()
df0_expanded['ID'] = pd.NA
df0_expanded['shop_id'] = pd.NA
df0_expanded['item_id'] = pd.NA

# Reorder columns to target schema
df0_expanded = df0_expanded[target_cols]

# Prepare df1 to match target schema: add missing columns with NaN
df1_expanded = pd.DataFrame(columns=target_cols)

# For df1, fill known columns and set others to NaN
df1_expanded['Store'] = pd.NA
df1_expanded['Dept'] = pd.NA
df1_expanded['Date'] = pd.NA
df1_expanded['Weekly_Sales'] = pd.NA
df1_expanded['IsHoliday'] = pd.NA
df1_expanded['ID'] = df1['ID']
df1_expanded['shop_id'] = df1['shop_id']
df1_expanded['item_id'] = df1['item_id']

# Concatenate the two dataframes (UNION)
df_final = pd.concat([df0_expanded, df1_expanded], ignore_index=True)

# Cast columns to target types
df_final['Store'] = pd.to_numeric(df_final['Store'], errors='coerce').astype('float')
df_final['Dept'] = pd.to_numeric(df_final['Dept'], errors='coerce').astype('float')
df_final['Date'] = df_final['Date'].astype('string')
df_final['Weekly_Sales'] = pd.to_numeric(df_final['Weekly_Sales'], errors='coerce').astype('float')
# IsHoliday in target examples is boolean-like but stored as string, so convert accordingly
df_final['IsHoliday'] = df_final['IsHoliday'].astype('string')
df_final['ID'] = pd.to_numeric(df_final['ID'], errors='coerce').astype('float')
df_final['shop_id'] = pd.to_numeric(df_final['shop_id'], errors='coerce').astype('float')
df_final['item_id'] = pd.to_numeric(df_final['item_id'], errors='coerce').astype('float')

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)