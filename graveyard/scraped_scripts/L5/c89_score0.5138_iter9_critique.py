import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

# Join Source5_89_4 with Source5_89_2 on Ord_id
merged = pd.merge(source4, source2, left_on="Ord_id", right_on="Ord_id", how="inner")

# Join with Source5_89_3 on Ship_id
merged = pd.merge(merged, source3, left_on="Ship_id", right_on="Ship_id", how="inner")

# Join with Source5_89_1 on Cust_id
merged = pd.merge(merged, source1, left_on="Cust_id", right_on="Cust_id", how="inner")

# Join with Source5_89_0 on Prod_id
merged = pd.merge(merged, source0, left_on="Prod_id", right_on="Prod_id", how="inner")

# Aggregate sum of Profit (no group by)
total_profit = merged["Profit"].sum()

# Create final DataFrame with one column Profit and one row (sum)
final = pd.DataFrame({"Profit": [total_profit]})

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)