import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_4.csv", index_col=0)

join_0 = pd.merge(source2, source0, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, source1, on="Ship_id", how="inner")
join_2 = pd.merge(join_1, source3, on="Ord_id", how="inner")
join_3 = pd.merge(join_2, source4, on="Prod_id", how="inner")

agg = join_3.groupby("Customer_Segment", as_index=False).agg({"Profit": "sum"})

final = agg[["Profit"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)