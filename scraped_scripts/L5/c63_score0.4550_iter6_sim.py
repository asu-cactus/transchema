import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

df = pd.merge(df4, df2[['Prod_id']], on='Prod_id', how='inner')
df = pd.merge(df, df0[['Ord_id']], on='Ord_id', how='inner')
df = pd.merge(df, df1[['Cust_id']], on='Cust_id', how='inner')
df = pd.merge(df, df3[['Ship_id']], on='Ship_id', how='inner')

df = df[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

df['Ord_id'] = df['Ord_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
df['Ship_id'] = df['Ship_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
df['Cust_id'] = df['Cust_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
df['Sales'] = df['Sales'].round().astype('Int64')
df['Discount'] = (df['Discount'] * 100).round().astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)