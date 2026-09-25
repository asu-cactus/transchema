import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, left_on=['Store', 'Dept'], right_on=['shop_id', 'item_id'], how='left')

df_merged = df_merged[['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']]

df_merged['Store'] = df_merged['Store'].astype(float)
df_merged['Dept'] = df_merged['Dept'].astype(float)
df_merged['Date'] = df_merged['Date'].astype(str)
df_merged['Weekly_Sales'] = df_merged['Weekly_Sales'].astype(float)
df_merged['IsHoliday'] = df_merged['IsHoliday'].astype(str)
df_merged['ID'] = pd.to_numeric(df_merged['ID'], errors='coerce')
df_merged['shop_id'] = pd.to_numeric(df_merged['shop_id'], errors='coerce')
df_merged['item_id'] = pd.to_numeric(df_merged['item_id'], errors='coerce')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)