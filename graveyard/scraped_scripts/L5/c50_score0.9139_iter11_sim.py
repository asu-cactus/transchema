import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

df = s4.merge(s0[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')
df = df.merge(s1[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')
df = df.merge(s2[['Prod_id']], on='Prod_id', how='inner')

df['Ship_Date'] = df['Ship_Date'].astype(str)

grouped = df.groupby('Ship_Date').agg(
    Ord_id=('Ord_id', 'count'),
    Prod_id=('Prod_id', pd.Series.nunique),
    Ship_id=('Ship_id', pd.Series.nunique)
).reset_index()

grouped['Ord_id'] = grouped['Ord_id'].astype(int)
grouped['Prod_id'] = grouped['Prod_id'].astype(int)
grouped['Ship_id'] = grouped['Ship_id'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)