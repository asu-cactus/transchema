import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

df = pd.merge(s1, s0, on="Ord_id")
df = pd.merge(df, s2, on="Cust_id")
df = pd.merge(df, s3, on="Prod_id")
df = pd.merge(df, s4, on="Ship_id")

def extract_num(x):
    if pd.isna(x):
        return pd.NA
    return int(''.join(filter(str.isdigit, str(x))))

df["ord_num"] = df["Ord_id"].map(extract_num)
df["prod_num"] = df["Prod_id"].map(extract_num)
df["ship_num"] = df["Ship_id"].map(extract_num)
df["cust_num"] = df["Cust_id"].map(extract_num)

df["Sales"] = pd.to_numeric(df["Sales"], errors='coerce').fillna(0).astype(int)
df["Discount"] = pd.to_numeric(df["Discount"], errors='coerce').fillna(0).astype(int)

result = df[["Product_Sub_Category", "ord_num", "prod_num", "ship_num", "cust_num", "Sales", "Discount"]].copy()
result.columns = ["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]

result = result.astype({
    "Product_Sub_Category": "string",
    "Ord_id": "Int64",
    "Prod_id": "Int64",
    "Ship_id": "Int64",
    "Cust_id": "Int64",
    "Sales": "Int64",
    "Discount": "Int64"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)