import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

join_0 = pd.merge(df4, df1, left_on="Ord_id", right_on="Ord_id", how="inner")
join_1 = pd.merge(join_0, df0, left_on="Ship_id", right_on="Ship_id", how="inner")
join_2 = pd.merge(join_1, df2, left_on="Cust_id", right_on="Cust_id", how="inner")
join_3 = pd.merge(join_2, df3, left_on="Prod_id", right_on="Prod_id", how="inner")

result = join_3.groupby("Sales", as_index=False).agg({"Sales": "sum"})

result = result[["Sales"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)