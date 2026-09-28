import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

join_0_2 = pd.merge(df2, df0, left_on="Ship_id", right_on="Ship_id", how="inner")
join_1 = pd.merge(join_0_2, df4, left_on="Ord_id", right_on="Ord_id", how="inner")
join_2 = pd.merge(join_1, df1, left_on="Cust_id", right_on="Cust_id", how="inner")
join_3 = pd.merge(join_2, df3, left_on="Prod_id", right_on="Prod_id", how="inner")

result = join_3.groupby("Profit", as_index=False).size().rename(columns={"size": "Profit"})
result = result.rename(columns={"Profit": "Profit"})
result["Profit"] = result["Profit"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)