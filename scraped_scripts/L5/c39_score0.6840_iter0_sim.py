import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

source0['Prod_id'] = source0['Prod_id'].str.replace('Prod_', '').astype(int)
source0['Ship_id'] = source0['Ship_id'].str.replace('SHP_', '').astype(int)
source0['Cust_id'] = source0['Cust_id'].str.replace('Cust_', '').astype(int)

source4['Prod_id'] = source4['Prod_id'].str.replace('Prod_', '').astype(int)

grouped_source0 = source0.groupby('Ord_id', as_index=False).first()

joined_0_4 = pd.merge(grouped_source0, source4[['Prod_id', 'Product_Category']], on='Prod_id', how='left')

final_df = pd.merge(joined_0_4[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']], source0[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']], on=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], how='left')

final_df = final_df[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)