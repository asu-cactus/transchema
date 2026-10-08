import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

joined_4_1 = pd.merge(source4, source1[['Ord_id', 'Order_Priority']], on='Ord_id', how='left')
joined_4_1_0 = pd.merge(joined_4_1, source0[['Ship_id', 'Ship_Mode']], on='Ship_id', how='left')
joined_4_1_0_2 = pd.merge(joined_4_1_0, source2[['Cust_id']], on='Cust_id', how='left')
final_join = pd.merge(joined_4_1_0_2, source3[['Prod_id']], on='Prod_id', how='left')

final = final_join[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)