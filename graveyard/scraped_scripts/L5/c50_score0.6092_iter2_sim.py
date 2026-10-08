import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

s0['Ship_id'] = s0['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
pivot = s0.pivot_table(index='Ship_Date', columns='Ship_Mode', values='Ship_id', aggfunc='first').reset_index()
# We only need Ship_Date and Ship_id, but Ship_id is per Ship_Mode, so we take the first non-null Ship_id per Ship_Date
pivot['Ship_id'] = pivot.drop(columns='Ship_Date').bfill(axis=1).iloc[:, 0]
pivot_result = pivot[['Ship_Date', 'Ship_id']]

s4['Ship_id'] = s4['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)

joined_1 = pd.merge(pivot_result, s4, on='Ship_id', how='inner')

s1['Ord_id'] = s1['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
joined_2 = pd.merge(joined_1, s1[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

s2['Prod_id'] = s2['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
final = pd.merge(joined_2, s2[['Prod_id']], on='Prod_id', how='inner')

final['Ship_Date'] = final['Ship_Date'].astype(str)
final = final[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)