import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

unpivot_cols = ['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin']
unpivot_result = df2.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=unpivot_cols, var_name='Measure', value_name='Value')

join_result_1 = pd.merge(unpivot_result, df4, left_on='Ord_id', right_on='Ord_id', how='left')
join_result_2 = pd.merge(join_result_1, df0, left_on='Order_ID', right_on='Order_ID', how='left')
join_result_3 = pd.merge(join_result_2, df1, left_on='Prod_id', right_on='Prod_id', how='left')
join_result_4 = pd.merge(join_result_3, df3, left_on='Cust_id', right_on='Cust_id', how='left')

result = join_result_4.loc[join_result_4['Measure'] == 'Profit', ['Value']].rename(columns={'Value': 'Profit'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)