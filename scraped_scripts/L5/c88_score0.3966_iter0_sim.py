import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

join_0 = pd.merge(df2, df0, on="Prod_id", how="inner")
join_1 = pd.merge(join_0, df1, left_on="Ship_id", right_on="Ship_id", how="inner")
join_2 = pd.merge(join_1, df3, left_on="Ord_id", right_on="Ord_id", how="inner")
join_3 = pd.merge(join_2, df4, left_on="Cust_id", right_on="Cust_id", how="inner")

result = join_3.groupby("Profit", as_index=False).size().rename(columns={"size": "count"})

# The target schema is only ['Profit'], so we just keep unique Profit values.
# Grouping by Profit and counting duplicates is not needed if we want just unique Profits.
# But the partial plan says GROUP_BY : [Profit], so we keep unique Profits.

final = pd.DataFrame({"Profit": join_3["Profit"].unique()})
final = final.sort_values("Profit").reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)