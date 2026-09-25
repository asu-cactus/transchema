import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

s1['Prod_id'] = s1['Prod_id'].str.replace('Prod_', '').astype(int)
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '').astype(int)
s1['Ord_id'] = s1['Ord_id'].str.replace('Ord_', '').astype(int)
s2['Ord_id'] = s2['Ord_id'].str.replace('Ord_', '').astype(int)
s0['Ship_id'] = s0['Ship_id'].str.replace('SHP_', '').astype(int)
s1['Ship_id'] = s1['Ship_id'].str.replace('SHP_', '').astype(int)
s1['Cust_id'] = s1['Cust_id'].str.replace('Cust_', '').astype(int)

join_1_4 = pd.merge(s1, s4[['Product_Sub_Category', 'Prod_id']], on='Prod_id', how='inner')
join_1_4_2 = pd.merge(join_1_4, s2[['Order_Date', 'Ord_id']], on='Ord_id', how='inner')
final_join = pd.merge(join_1_4_2, s0[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')

final = final_join.rename(columns={'Ship_Date': 'Order_Date'})
final = final[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

final['Order_Date'] = final['Order_Date'].astype(str)
final['Ord_id'] = final['Ord_id'].astype(int)
final['Prod_id'] = final['Prod_id'].astype(int)
final['Ship_id'] = final['Ship_id'].astype(int)
final['Cust_id'] = final['Cust_id'].astype(int)
final['Sales'] = final['Sales'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)