import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

join1 = pd.merge(df3, df2, on="Ord_id", how="inner")
join2 = pd.merge(join1, df1, on="Ship_id", how="inner")
join3 = pd.merge(join2, df0, on="Cust_id", how="inner")
join4 = pd.merge(join3, df4, on="Prod_id", how="inner")

# Aggregate sum of Profit column without grouping
total_profit = join4["Profit"].sum()

final = pd.DataFrame({"Profit": [total_profit]})

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)