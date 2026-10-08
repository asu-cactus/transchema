import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_51/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_51/training_4.csv", index_col=0)

df = pd.merge(s4, s1, on="Ship_id", how="inner")
df = pd.merge(df, s3, on="Prod_id", how="inner")

# The second join with s4 again on Ord_id is redundant because s4 is already included.
# Instead, we just keep the columns needed.

# Group by Ship_Mode and aggregate Ord_id, Prod_id, Ship_id by count of unique values or by count of rows?
# Target examples show Ord_id, Prod_id, Ship_id values equal to Ship_Mode counts.
# So we count distinct Ord_id, Prod_id, Ship_id per Ship_Mode.

agg_df = df.groupby("Ship_Mode").agg(
    Ord_id = ("Ord_id", "nunique"),
    Prod_id = ("Prod_id", "nunique"),
    Ship_id = ("Ship_id", "nunique")
).reset_index()

agg_df["Ord_id"] = agg_df["Ord_id"].astype(int)
agg_df["Prod_id"] = agg_df["Prod_id"].astype(int)
agg_df["Ship_id"] = agg_df["Ship_id"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_51/target_multisource_mcts.csv", index=False)