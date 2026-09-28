import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

joined = pd.merge(source2, source4, on="Ord_id")

result = joined.groupby("Profit", as_index=False).size()

# The target schema is ['Profit': float], and target examples show Profit values aggregated.
# The partial plan suggests grouping by Profit, but grouping by a float column to aggregate counts is unusual.
# Instead, we interpret the partial plan as grouping by Profit to get unique Profit values (like distinct).
# The target examples show Profit values only, so we output unique Profit values.

# Extract unique Profit values as float
final = pd.DataFrame({"Profit": joined["Profit"].astype(float).unique()})
final = final.sort_values("Profit").reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)