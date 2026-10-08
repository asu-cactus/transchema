import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city")

grouped = merged.groupby("city").agg(
    driver_count=pd.NamedAgg(column="driver_count", aggfunc="sum"),
    fare=pd.NamedAgg(column="fare", aggfunc="mean"),
    ride_id=pd.NamedAgg(column="ride_id", aggfunc="mean"),
).reset_index()

grouped["driver_count"] = grouped["driver_count"].astype(int)
grouped["fare"] = grouped["fare"].astype(float)
grouped["ride_id"] = grouped["ride_id"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)