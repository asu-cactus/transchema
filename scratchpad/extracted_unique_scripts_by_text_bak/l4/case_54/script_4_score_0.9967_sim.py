import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

g0 = df0.groupby("WhereFought").size().reset_index(name="count0")
g1 = df1.groupby("WhereFought").size().reset_index(name="count1")
g2 = df2.groupby("WhereFought").size().reset_index(name="count2")
g3 = df3.groupby("WhereFought").size().reset_index(name="count3")

merged = g0.merge(g1, on="WhereFought", how="outer")
merged = merged.merge(g2, on="WhereFought", how="outer")
merged = merged.merge(g3, on="WhereFought", how="outer")

merged = merged.fillna(0)
merged["WarNum"] = merged[["count0", "count1", "count2", "count3"]].sum(axis=1).astype(int)
result = merged[["WhereFought", "WarNum"]].copy()
result["WhereFought"] = result["WhereFought"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)