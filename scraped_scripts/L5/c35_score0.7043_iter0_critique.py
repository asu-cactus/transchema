import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

df = s0.merge(s1, on="Prod_id", how="left")
df = df.merge(s3, on="Cust_id", how="left")
df = df.merge(s4, on="Ord_id", how="left")

def extract_int(prefix, s):
    return s.str.replace(prefix, "", regex=False).astype(int)

df["Ord_id"] = extract_int("Ord_", df["Ord_id"])
df["Prod_id"] = extract_int("Prod_", df["Prod_id"])
df["Cust_id"] = extract_int("Cust_", df["Cust_id"])

# Sales rounded and converted to int for aggregation
df["Sales"] = df["Sales"].round().astype(int)

# Group by the leftmost columns that likely form the unique key
result = df.groupby(
    ["Product_Category", "Ship_id", "Ord_id", "Prod_id", "Cust_id"],
    as_index=False,
).agg({"Sales": "sum"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)