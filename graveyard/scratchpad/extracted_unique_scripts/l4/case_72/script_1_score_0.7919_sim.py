import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

grouped = merged.groupby("city").agg(
    a=pd.NamedAgg(column="fare", aggfunc="mean"),
    b=pd.NamedAgg(column="driver_count", aggfunc="sum")
).reset_index()

grouped["a"] = grouped["a"].astype(float)
grouped["b"] = grouped["b"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)