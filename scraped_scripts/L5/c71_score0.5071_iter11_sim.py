import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="Cust_id", how="inner")
join_012 = pd.merge(join_01, source2, on="Ship_id", how="inner")
join_0123 = pd.merge(join_012, source3, on="Prod_id", how="inner")
join_01234 = pd.merge(join_0123, source4, on="Ord_id", how="inner")

result = join_01234[["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

result["Sales"] = result["Sales"].astype(int)
result["Discount"] = (result["Discount"] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)