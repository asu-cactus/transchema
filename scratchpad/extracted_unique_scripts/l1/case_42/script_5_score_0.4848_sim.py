import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

grouped = df0.groupby("item_id").agg(
    user_id_count=pd.NamedAgg(column="user_id", aggfunc="count"),
    rating_avg=pd.NamedAgg(column="rating", aggfunc="mean"),
    timestamp_min=pd.NamedAgg(column="timestamp", aggfunc="min"),
    timestamp_max=pd.NamedAgg(column="timestamp", aggfunc="max"),
).reset_index()

merged = pd.merge(grouped, df1[["item_id", "movie title"]], on="item_id", how="inner")

result = pd.DataFrame()
result["user_id"] = merged["user_id_count"].astype(int)
result["item_id"] = merged["item_id"].astype(int)
result["rating"] = merged["rating_avg"].round().astype(int)
result["timestamp"] = merged["timestamp_min"].astype(int)
result["movie title"] = merged["movie title"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)