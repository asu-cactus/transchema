import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

merged = df4.merge(df1, on="Ord_id").merge(df2, on="Ship_id").merge(df0, on="Cust_id").merge(df3, on="Prod_id")

profit_series = merged["Profit"]

result = profit_series.groupby(profit_series).sum().reset_index(drop=True)
result = pd.DataFrame(profit_series.values, columns=["Profit"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)