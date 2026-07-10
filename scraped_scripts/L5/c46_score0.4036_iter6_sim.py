import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

j1 = pd.merge(s4, s3, on="Prod_id", how="inner")
j2 = pd.merge(j1, s0, left_on="Cust_id", right_on="Cust_id", how="inner")
j3 = pd.merge(j2, s2, left_on="Ord_id", right_on="Ord_id", how="inner")
j4 = pd.merge(j3, s1, left_on="Ship_id", right_on="Ship_id", how="inner")

result = j4[["Customer_Name", "Ord_id", "Prod_id", "Ship_id"]].copy()

def to_int_strip_prefix(series, prefix):
    return series.str.replace(prefix, "", regex=False).astype(int)

result["Ord_id"] = to_int_strip_prefix(result["Ord_id"], "Ord_")
result["Prod_id"] = to_int_strip_prefix(result["Prod_id"], "Prod_")
result["Ship_id"] = to_int_strip_prefix(result["Ship_id"], "SHP_")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)