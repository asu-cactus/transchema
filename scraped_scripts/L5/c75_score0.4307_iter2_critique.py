import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_4.csv", index_col=0)

# Join Source0 and Source1 on Prod_id
joined_01 = pd.merge(source0, source1, on="Prod_id")

# Join with Source2 on Ship_id
joined_02 = pd.merge(joined_01, source2, on="Ship_id")

# Join with Source3 on Ord_id
joined_03 = pd.merge(joined_02, source3, on="Ord_id")

# Join with Source4 on Cust_id
joined_all = pd.merge(joined_03, source4, on="Cust_id")

# Group by Region and Order_Priority, aggregate sum of Profit
agg = joined_all.groupby(["Region", "Order_Priority"], dropna=False)["Profit"].sum().reset_index()

# Output only the Profit column as per target schema
result = agg[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)