import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

unpivoted_source4 = source4.melt(
    id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'],
    value_vars=['Sales', 'Discount'],
    var_name='Measure',
    value_name='Value'
)

sales_df = unpivoted_source4[unpivoted_source4['Measure'] == 'Sales'].copy()
discount_df = unpivoted_source4[unpivoted_source4['Measure'] == 'Discount'].copy()

merged = source4[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

joined_0_1 = pd.merge(merged, source0[['Ord_id', 'Order_Date']], on='Ord_id', how='left')
joined_0_1_2 = pd.merge(joined_0_1, source1[['Ship_id']], on='Ship_id', how='left')
joined_0_1_2_3 = pd.merge(joined_0_1_2, source2[['Cust_id']], on='Cust_id', how='left')
final_join = pd.merge(joined_0_1_2_3, source3[['Prod_id']], on='Prod_id', how='left')

final = final_join[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

final['Ord_id'] = final['Ord_id'].str.extract(r'(\d+)').astype('Int64')
final['Prod_id'] = final['Prod_id'].str.extract(r'(\d+)').astype('Int64')
final['Ship_id'] = final['Ship_id'].str.extract(r'(\d+)').astype('Int64')
final['Cust_id'] = final['Cust_id'].str.extract(r'(\d+)').astype('Int64')
final['Sales'] = final['Sales'].round().astype('Int64')
final['Discount'] = (final['Discount'] * 100).round().astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)