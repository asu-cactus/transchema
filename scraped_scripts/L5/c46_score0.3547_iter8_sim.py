import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

df0_pivot = df0[['Customer_Name', 'Cust_id']].drop_duplicates().rename(columns={'Cust_id':'Cust_id'})
# Group by Customer_Name to ensure unique mapping (pivot implied)
df0_grouped = df0_pivot.groupby('Customer_Name', as_index=False).first()

df = pd.merge(df4, df0_grouped, left_on='Cust_id', right_on='Cust_id', how='left')

df = pd.merge(df, df2[['Ord_id']], on='Ord_id', how='left')
df = pd.merge(df, df3[['Prod_id']], on='Prod_id', how='left')
df = pd.merge(df, df1[['Ship_id']], on='Ship_id', how='left')

result = df[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)