import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=['Sales', 'Discount'], var_name='Measure', value_name='Value')

df_join_1 = pd.merge(df1_unpivot, df3[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='left')

df_join_2 = pd.merge(df_join_1, df0[['Ord_id']], on='Ord_id', how='left')

df_join_3 = pd.merge(df_join_2, df4[['Ship_id']], on='Ship_id', how='left')

df_join_4 = pd.merge(df_join_3, df2[['Cust_id']], on='Cust_id', how='left')

df_pivot = df_join_4.pivot_table(index=['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], columns='Measure', values='Value', aggfunc='sum').reset_index()

df_pivot.columns.name = None

df_pivot['Sales'] = df_pivot['Sales'].fillna(0).astype(int)
df_pivot['Discount'] = df_pivot['Discount'].fillna(0).astype(int)

df_pivot = df_pivot[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)