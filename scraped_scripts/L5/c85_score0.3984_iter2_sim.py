import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

merged = pd.merge(source4, source2, left_on="Cust_id", right_on="Cust_id")

result = merged.groupby("Cust_id", as_index=False)["Sales"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)