import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

merged_1 = pd.merge(source2, source0, on="Prod_id")
merged_2 = pd.merge(merged_1, source1, on="Ship_id")
merged_3 = pd.merge(merged_2, source3, on="Ord_id")
merged_4 = pd.merge(merged_3, source4, on="Cust_id")

result = merged_4.groupby("Product_Category", as_index=False).agg({"Profit": "mean"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)