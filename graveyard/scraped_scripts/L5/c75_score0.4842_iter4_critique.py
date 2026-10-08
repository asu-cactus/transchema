import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_4.csv", index_col=0)

# Join Source0 with Source1 on Prod_id
merged_01 = pd.merge(source0, source1, left_on="Prod_id", right_on="Prod_id", how="inner")

# Join merged_01 with Source3 on Ord_id
merged_013 = pd.merge(merged_01, source3, left_on="Ord_id", right_on="Ord_id", how="inner")

# Join merged_013 with Source2 on Ship_id
merged_0132 = pd.merge(merged_013, source2, left_on="Ship_id", right_on="Ship_id", how="inner")

# Join merged_0132 with Source4 on Cust_id
merged_all = pd.merge(merged_0132, source4, left_on="Cust_id", right_on="Cust_id", how="inner")

# Aggregate sum of Profit (no group by)
result = pd.DataFrame()
result["Profit"] = [merged_all["Profit"].sum()]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)