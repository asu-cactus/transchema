import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

agg_df1 = df1.groupby("city").agg(
    fare_min=pd.NamedAgg(column="fare", aggfunc="min"),
    fare_max=pd.NamedAgg(column="fare", aggfunc="max"),
    ride_id_count_distinct=pd.NamedAgg(column="ride_id", aggfunc=lambda x: x.nunique())
).reset_index()

agg_df1["fare"] = (agg_df1["fare_min"] + agg_df1["fare_max"]) / 2
agg_df1 = agg_df1[["city", "fare", "ride_id_count_distinct"]].rename(columns={"ride_id_count_distinct": "ride_id"})

merged = pd.merge(df0, agg_df1, how="inner", on="city")

result = merged[["city", "driver_count", "fare", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)