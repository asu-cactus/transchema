import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)

s0_sel = s0[['Order_Date', 'Ord_id']]
s4_sel = s4[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

union_result = pd.concat([s0_sel, s4_sel], ignore_index=True, sort=False)

join_result_1 = union_result.merge(s1[['Ship_id']], on='Ship_id', how='left') if 'Ship_id' in union_result.columns else union_result.merge(s1[['Ship_id']], left_on='Ship_id', right_on='Ship_id', how='left')
if 'Ship_id' not in union_result.columns:
    join_result_1 = union_result.merge(s1[['Ship_id']], left_on='Ship_id', right_on='Ship_id', how='left')
else:
    join_result_1 = union_result.merge(s1[['Ship_id']], on='Ship_id', how='left')

join_result_1 = union_result.merge(s1[['Ship_id']], on='Ship_id', how='left') if 'Ship_id' in union_result.columns else union_result

join_result_1 = union_result.merge(s1[['Ship_id']], on='Ship_id', how='left')

join_result_2 = join_result_1.merge(s2[['Cust_id']], on='Cust_id', how='left')
join_result_3 = join_result_2.merge(s3[['Prod_id']], on='Prod_id', how='left')

final = join_result_3[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

final['Ord_id'] = final['Ord_id'].str.replace('Ord_', '').astype('Int64')
final['Prod_id'] = final['Prod_id'].str.replace('Prod_', '').astype('Int64')
final['Ship_id'] = final['Ship_id'].str.replace('SHP_', '').astype('Int64')
final['Cust_id'] = final['Cust_id'].str.replace('Cust_', '').astype('Int64')
final['Sales'] = final['Sales'].round().astype('Int64')
final['Discount'] = (final['Discount'] * 100).round().astype('Int64')
final['Order_Date'] = final['Order_Date'].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)