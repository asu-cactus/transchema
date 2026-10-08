import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

join_1 = pd.merge(source2, source0, left_on="Ship_id", right_on="Ship_id", how="inner")
join_2 = pd.merge(join_1, source1, left_on="Prod_id", right_on="Prod_id", how="inner")
join_3 = pd.merge(join_2, source3, left_on="Cust_id", right_on="Cust_id", how="inner")
join_4 = pd.merge(join_3, source4, left_on="Ord_id", right_on="Ord_id", how="inner")

total_profit = join_4["Profit"].sum()

result = pd.DataFrame({"Profit": [total_profit]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)