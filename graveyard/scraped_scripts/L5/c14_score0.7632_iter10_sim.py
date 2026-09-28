import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

join_1 = pd.merge(source2, source1, on="Ship_id", how="inner")
join_2 = pd.merge(join_1, source4, on="Ord_id", how="inner")
join_3 = pd.merge(join_2, source0, on="Cust_id", how="inner")
join_4 = pd.merge(join_3, source3, on="Prod_id", how="inner")

result = join_4[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)