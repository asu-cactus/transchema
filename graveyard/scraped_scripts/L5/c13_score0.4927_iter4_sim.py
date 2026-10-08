import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

union_3 = pd.concat([source3, source3], ignore_index=True)

join_1 = pd.merge(union_3, source1, on="Prod_id", how="inner")

join_2 = pd.merge(join_1, source0, on="Ord_id", how="inner")

join_3 = pd.merge(join_2, source4, on="Ship_id", how="inner")

join_4 = pd.merge(join_3, source2, on="Cust_id", how="inner")

result = join_4[["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)