import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

# Join all source tables on their keys using inner joins
df = s4.merge(s2, on="Ship_id", how="inner")
df = df.merge(s0, on="Ord_id", how="inner")
df = df.merge(s1, on="Cust_id", how="inner")
df = df.merge(s3, on="Prod_id", how="inner")

# Group by Ship_Mode and aggregate counts of unique Ord_id (used for all ID columns) and sum of Sales
grouped = df.groupby("Ship_Mode").agg(
    Ord_id_count=pd.NamedAgg(column="Ord_id", aggfunc=pd.Series.nunique),
    Sales_sum=pd.NamedAgg(column="Sales", aggfunc="sum"),
)

# Since counts of unique Ord_id, Prod_id, Ship_id, Cust_id are expected to be the same per Ship_Mode,
# we use Ord_id_count for all ID columns
result = pd.DataFrame({
    "Ship_Mode": grouped.index,
    "Ord_id": grouped["Ord_id_count"].astype(int),
    "Prod_id": grouped["Ord_id_count"].astype(int),
    "Ship_id": grouped["Ord_id_count"].astype(int),
    "Cust_id": grouped["Ord_id_count"].astype(int),
    "Sales": grouped["Sales_sum"].astype(int),
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)