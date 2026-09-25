import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

df = pd.merge(source1, source0[['Prod_id']], on='Prod_id', how='inner')
df = pd.merge(df, source3[['Cust_id']], on='Cust_id', how='inner')
df = pd.merge(df, source4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')
df = pd.merge(df, source2[['Ord_id']], on='Ord_id', how='inner')

agg = df.groupby(['Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum'
})

agg['Order_Quantity'] = agg['Order_Quantity'].astype(int)
agg['Sales'] = agg['Sales'].round().astype(int)
agg = agg.rename(columns={'Order_Quantity': 'Order_Quantity', 'Sales': 'Sales'})

agg = agg[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)