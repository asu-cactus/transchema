import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

df = pd.merge(source4, source0, on="Ship_id", how="inner")
df = pd.merge(df, source1, on="Ord_id", how="inner")
df = pd.merge(df, source2, on="Cust_id", how="inner")
df = pd.merge(df, source3, on="Prod_id", how="inner")

agg_df = df.groupby(
    ["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False
).agg({
    "Sales": "sum",
    "Discount": "sum"
})

agg_df["Sales"] = agg_df["Sales"].round().astype("Int64")
agg_df["Discount"] = agg_df["Discount"].round().astype("Int64")

agg_df = agg_df[["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)