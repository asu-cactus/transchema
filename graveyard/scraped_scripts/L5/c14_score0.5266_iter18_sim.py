import pandas as pd

src2_path = "autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv"

df2_1 = pd.read_csv(src2_path, index_col=0)
df2_2 = pd.read_csv(src2_path, index_col=0)

df_union = pd.concat([df2_1, df2_2], ignore_index=True)

df_union['Ship_id'] = df_union['Ship_id'].astype(str)
df_union['Ord_id'] = df_union['Ord_id'].str.replace('Ord_', '').astype(int)
df_union['Prod_id'] = df_union['Prod_id'].str.replace('Prod_', '').astype(int)
df_union['Cust_id'] = df_union['Cust_id'].str.replace('Cust_', '').astype(int)

df_target = df_union[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)