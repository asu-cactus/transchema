import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_4.csv", index_col=0)

join_0 = pd.merge(source2, source0, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, source1, left_on="Ship_id", right_on="Ship_id", how="inner")
join_2 = pd.merge(join_1, source3, left_on="Ord_id", right_on="Ord_id", how="inner")
join_3 = pd.merge(join_2, source4, left_on="Prod_id", right_on="Prod_id", how="inner")

result = join_3.groupby("Profit", as_index=False).size().rename(columns={"size": "count"})

# The target schema is only ['Profit'], so we just keep the Profit column grouped by itself.
# Grouping by Profit alone returns unique Profit values, so we select Profit column only.
final = result[["Profit"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)