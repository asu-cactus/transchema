import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

join_0 = pd.merge(df4, df0, on="Prod_id", how="inner")
join_1 = pd.merge(join_0, df1, on="Cust_id", how="inner")
join_2 = pd.merge(join_1, df2, left_on="Ord_id", right_on="Ord_id", how="inner")
join_3 = pd.merge(join_2, df3, on="Ship_id", how="inner")

result = join_3.groupby("Profit", as_index=False).size()
# The target schema is only ['Profit': float], and target examples show Profit values aggregated counts? 
# But the partial plan says GROUP_BY : [Profit], which implies grouping by Profit (which is float) and counting rows per Profit.
# However, grouping by float Profit is unusual. The target examples show Profit values as floats, not counts.
# The target examples show Profit values as floats, no count column.
# So likely the target is just the distinct Profit values from the joined data.
# The partial plan is ambiguous, but since target schema is only Profit (float), and partial plan says GROUP_BY : [Profit], 
# the best interpretation is to get unique Profit values (group by Profit) and output them.

# So we just get unique Profit values sorted ascending
final = pd.DataFrame({"Profit": sorted(join_3["Profit"].dropna().unique())})

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)