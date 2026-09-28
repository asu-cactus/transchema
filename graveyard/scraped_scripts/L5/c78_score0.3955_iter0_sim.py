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

result = join4.groupby("Profit", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires 'Profit' column, so we keep unique Profit values.
# The GROUP_BY : [Profit] implies grouping by Profit, but target only has Profit column.
# So we just take unique Profit values (grouping by Profit) without aggregation.
# Since the target examples show Profit values only, we output unique Profit values.

final = pd.DataFrame({"Profit": join4["Profit"].unique()})
final = final.sort_values("Profit").reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)