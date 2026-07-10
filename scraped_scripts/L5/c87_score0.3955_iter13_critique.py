import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

# Join Source5_87_0 and Source5_87_4 on Order_ID
joined_0_4 = pd.merge(source0, source4, on="Order_ID")

# Join the above with Source5_87_2 on Ord_id
joined_0_4_2 = pd.merge(joined_0_4, source2, on="Ord_id")

# Join the above with Source5_87_1 on Prod_id
joined_0_4_2_1 = pd.merge(joined_0_4_2, source1, on="Prod_id")

# Join the above with Source5_87_3 on Cust_id
final_joined = pd.merge(joined_0_4_2_1, source3, on="Cust_id")

# Project Profit column only
result = final_joined[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)