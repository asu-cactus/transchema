import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

merged = df4.merge(df1, on='Ord_id', how='left')\
            .merge(df0, on='Ship_id', how='left')\
            .merge(df2, on='Cust_id', how='left')\
            .merge(df3, on='Prod_id', how='left')

result = merged.groupby('Ord_id', as_index=False).agg({'Sales': 'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)