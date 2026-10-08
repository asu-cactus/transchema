import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

# Join source4 with source1 on Cust_id
joined = pd.merge(source4, source1, left_on="Cust_id", right_on="Cust_id")

# Join with source0 on Prod_id
joined = pd.merge(joined, source0, left_on="Prod_id", right_on="Prod_id")

# Join with source2 on Ord_id
joined = pd.merge(joined, source2, left_on="Ord_id", right_on="Ord_id")

# Join with source3 on Ship_id
joined = pd.merge(joined, source3, left_on="Ship_id", right_on="Ship_id")

# Group by Region and sum Profit
result = joined.groupby("Region", as_index=False).agg({"Profit": "sum"})

# Output only Profit column as per target schema
result = result[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)