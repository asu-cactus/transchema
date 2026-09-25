import pandas as pd

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)
df_unpivot = df4.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], 
                      value_vars=['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin'],
                      var_name='Measure', value_name='Value')
df_profit = df_unpivot[df_unpivot['Measure'] == 'Profit']
result = df_profit[['Value']].rename(columns={'Value': 'Profit'})
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)