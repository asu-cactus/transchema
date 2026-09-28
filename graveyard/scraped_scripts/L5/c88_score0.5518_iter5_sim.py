import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

joined = pd.merge(source2, source4, left_on="Cust_id", right_on="Cust_id")

result = joined.groupby("Profit", dropna=False, as_index=False).size()

# The target schema is ['Profit': float], so we only keep Profit column.
# The groupby on Profit with size() returns counts, but target only has Profit column.
# The partial plan says GROUP_BY : [Profit], which implies grouping by Profit.
# Since target only has Profit column, we just keep unique Profit values.

result = joined[["Profit"]].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)