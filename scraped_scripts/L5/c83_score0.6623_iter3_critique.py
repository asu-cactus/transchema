import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

df = src4.merge(src0, on='Cust_id', how='inner') \
         .merge(src1, on='Ord_id', how='inner') \
         .merge(src2, on='Ship_id', how='inner') \
         .merge(src3, on='Prod_id', how='inner')

df['Profit'] = df['Profit'].astype(float)

agg_df = df.groupby('Customer_Segment', as_index=False).agg({'Profit': 'sum'})

result = agg_df[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)