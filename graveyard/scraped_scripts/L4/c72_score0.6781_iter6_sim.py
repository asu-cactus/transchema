import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

agg = merged.groupby(["city", "type"]).agg(
    a=pd.NamedAgg(column="driver_count", aggfunc="sum"),
    b=pd.NamedAgg(column="ride_id", aggfunc="count")
).reset_index()

result = agg.groupby("city").agg(
    a=pd.NamedAgg(column="a", aggfunc="mean"),
    b=pd.NamedAgg(column="b", aggfunc="sum")
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)