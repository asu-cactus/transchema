import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, left_on=['Store', 'Dept'], right_on=['shop_id', 'item_id'], how='inner')

result = pd.DataFrame()
result['Store'] = merged['Store'].astype(float)
result['Dept'] = merged['Dept'].astype(float)
result['Date'] = merged['Date'].astype(str)
result['Weekly_Sales'] = merged['Weekly_Sales'].astype(float)
result['IsHoliday'] = merged['IsHoliday'].astype(str)
result['ID'] = merged['ID'].astype(float)
result['shop_id'] = merged['shop_id'].astype(float)
result['item_id'] = merged['item_id'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)