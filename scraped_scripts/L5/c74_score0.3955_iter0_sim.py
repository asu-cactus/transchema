import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)

df = pd.merge(df4, df0, on="Prod_id", how="inner")
df = pd.merge(df, df1, left_on="Ord_id", right_on="Ord_id", how="inner")
df = pd.merge(df, df2, left_on="Cust_id", right_on="Cust_id", how="inner")
df = pd.merge(df, df3, left_on="Ship_id", right_on="Ship_id", how="inner")

result = df.groupby("Profit", as_index=False).agg({"Profit":"sum"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)