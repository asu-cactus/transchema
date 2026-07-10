import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

df = pd.merge(s4, s0[['Ord_id', 'Order_Date']], on='Ord_id', how='left')
df = pd.merge(df, s1[['Ship_id']], on='Ship_id', how='left')
df = pd.merge(df, s2[['Cust_id']], on='Cust_id', how='left')
df = pd.merge(df, s3[['Prod_id']], on='Prod_id', how='left')

df_grouped = df.groupby('Order_Date', as_index=False).agg({
    'Ord_id': 'count',
    'Prod_id': 'count',
    'Ship_id': 'count',
    'Cust_id': 'count',
    'Sales': 'sum',
    'Discount': 'sum'
})

df_grouped = df_grouped.rename(columns={
    'Ord_id': 'Ord_id',
    'Prod_id': 'Prod_id',
    'Ship_id': 'Ship_id',
    'Cust_id': 'Cust_id',
    'Sales': 'Sales',
    'Discount': 'Discount'
})

df_grouped['Order_Date'] = df_grouped['Order_Date'].astype(str)
df_grouped['Ord_id'] = df_grouped['Ord_id'].astype(int)
df_grouped['Prod_id'] = df_grouped['Prod_id'].astype(int)
df_grouped['Ship_id'] = df_grouped['Ship_id'].astype(int)
df_grouped['Cust_id'] = df_grouped['Cust_id'].astype(int)
df_grouped['Sales'] = df_grouped['Sales'].round().astype(int)
df_grouped['Discount'] = df_grouped['Discount'].round().astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)