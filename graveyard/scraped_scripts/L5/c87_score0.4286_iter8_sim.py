import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)

join_0_4 = pd.merge(s0, s4, left_on="Order_ID", right_on="Order_ID")
joined = pd.merge(join_0_4, s2, left_on="Ord_id", right_on="Ord_id")

result = joined.groupby("Profit", dropna=False, as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires 'Profit' column, so we select unique Profit values.
# The GROUP_BY : [Profit] implies grouping by Profit, but no aggregation specified.
# Since target schema is only Profit (float), we just get unique Profit values.
# So we take the distinct Profit values from joined data.

final = joined[["Profit"]].drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)