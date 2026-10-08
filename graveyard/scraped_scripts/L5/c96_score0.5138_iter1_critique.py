import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_4.csv", index_col=0)

join_0 = pd.merge(df2, df0, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, df1, on="Ship_id", how="inner")
join_2 = pd.merge(join_1, df3, on="Ord_id", how="inner")
join_3 = pd.merge(join_2, df4, on="Prod_id", how="inner")

result = pd.DataFrame({'Profit': [join_3['Profit'].sum()]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)