import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)

join_1 = pd.merge(source2, source0, on="Cust_id", how="inner")
join_2 = pd.merge(join_1, source1, on="Ship_id", how="inner")

result = join_2[["Ship_Date", "Customer_Name", "Ord_id", "Prod_id", "Ship_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)