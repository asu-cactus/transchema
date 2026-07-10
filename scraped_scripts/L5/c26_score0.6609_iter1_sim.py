import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

df1_2 = pd.merge(source1, source2, how='inner', on='Ord_id')
df1_2_4 = pd.merge(df1_2, source4, how='inner', on='Prod_id')
df1_2_4_0 = pd.merge(df1_2_4, source0, how='inner', on='Ship_id')
df_final = pd.merge(df1_2_4_0, source3, how='inner', on='Cust_id')

df_final['Ord_id'] = df_final['Ord_id'].str.replace('Ord_', '').astype(int)
df_final['Prod_id'] = df_final['Prod_id'].str.replace('Prod_', '').astype(int)
df_final['Ship_id'] = df_final['Ship_id'].str.replace('SHP_', '').astype(int)
df_final['Cust_id'] = df_final['Cust_id'].str.replace('Cust_', '').astype(int)
df_final['Order_Date'] = df_final['Order_Date'].astype(str)
df_final['Sales'] = df_final['Sales'].round().astype(int)

result = df_final[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)