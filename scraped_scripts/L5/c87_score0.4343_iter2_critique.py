import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

# Join Source5_87_2 and Source5_87_4 on Ord_id
joined = pd.merge(source2, source4, on="Ord_id")

# Join with Source5_87_1 on Prod_id
joined = pd.merge(joined, source1, on="Prod_id")

# Join with Source5_87_3 on Cust_id
joined = pd.merge(joined, source3, on="Cust_id")

# Join with Source5_87_0 on Ship_id
joined = pd.merge(joined, source0, on="Ship_id")

# Group by Ord_id and aggregate mean of Profit
agg = joined.groupby("Ord_id", as_index=False).agg({"Profit": "mean"})

# Output only Profit column as per target schema
final = agg[["Profit"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)