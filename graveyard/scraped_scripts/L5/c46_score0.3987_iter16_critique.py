import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

join_1 = pd.merge(source4, source3, on="Prod_id", how="inner")
join_2 = pd.merge(join_1, source0, on="Cust_id", how="inner")
join_3 = pd.merge(join_2, source1, on="Ship_id", how="inner")
join_4 = pd.merge(join_3, source2, on="Ord_id", how="inner")

result = join_4[["Customer_Name", "Ord_id", "Prod_id", "Ship_id"]].copy()

def to_int_strip_prefix(series, prefix):
    return series.str.replace(prefix, "", regex=False).astype(int)

result["Ord_id"] = to_int_strip_prefix(result["Ord_id"], "Ord_")
result["Prod_id"] = to_int_strip_prefix(result["Prod_id"], "Prod_")
result["Ship_id"] = to_int_strip_prefix(result["Ship_id"], "SHP_")

# Group by all columns to remove duplicates, aggregate by count on Ord_id
grouped = result.groupby(["Customer_Name", "Ord_id", "Prod_id", "Ship_id"], as_index=False).agg({"Ord_id": "count"})

# Drop the aggregation column to match target schema
final_result = grouped[["Customer_Name", "Ord_id", "Prod_id", "Ship_id"]]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)