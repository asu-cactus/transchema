import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

df = pd.merge(source2, source1, on="Ship_id", how="inner")
df = pd.merge(df, source0[["Prod_id"]], on="Prod_id", how="inner")
df = pd.merge(df, source3[["Cust_id"]], on="Cust_id", how="inner")
df = pd.merge(df, source4[["Ord_id"]], on="Ord_id", how="inner")

grouped = df.groupby(["Ship_Date", "Prod_id"]).agg(
    Ord_id_count=pd.NamedAgg(column="Ord_id", aggfunc="count"),
    Ship_id_count=pd.NamedAgg(column="Ship_id", aggfunc="count"),
    Cust_id_count=pd.NamedAgg(column="Cust_id", aggfunc="count"),
).reset_index()

grouped = grouped.rename(columns={
    "Ship_Date": "Ship_Date",
    "Prod_id": "Prod_id",
    "Ord_id_count": "Ord_id",
    "Ship_id_count": "Ship_id",
    "Cust_id_count": "Cust_id"
})

grouped["Ord_id"] = grouped["Ord_id"].astype(int)
grouped["Ship_id"] = grouped["Ship_id"].astype(int)
grouped["Cust_id"] = grouped["Cust_id"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)