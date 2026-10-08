import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

joined_2_1 = pd.merge(source2, source1, how='inner', left_on='Prod_id', right_on='Prod_id')
joined_2_1_4 = pd.merge(joined_2_1, source4, how='inner', left_on='Ord_id', right_on='Ord_id')
joined_2_1_4_0 = pd.merge(joined_2_1_4, source0, how='inner', left_on='Cust_id', right_on='Cust_id')
final_join = pd.merge(joined_2_1_4_0, source3, how='inner', left_on='Ship_id', right_on='Ship_id')

final = final_join[['Ship_id', 'Order_Priority', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales', 'Discount']]

final['Ord_id'] = final['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
final['Prod_id'] = final['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
final['Cust_id'] = final['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
final['Ship_id'] = final['Ship_id'].astype(str)
final['Order_Priority'] = final['Order_Priority'].astype(str)

# Aggregate Sales and Discount by sum grouped by the leftmost key columns
final = final.groupby(['Ship_id', 'Order_Priority', 'Ord_id', 'Prod_id', 'Cust_id'], as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

final['Sales'] = final['Sales'].astype(int)
final['Discount'] = final['Discount'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)