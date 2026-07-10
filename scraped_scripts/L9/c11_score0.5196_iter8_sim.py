import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv", index_col=0)

agg = s7.groupby("2012-12-05", as_index=False).agg({
    "301.0": "sum"
})
agg_6 = s6.groupby("2012-12-05", as_index=False).agg({"242.364": "sum"})
agg_3 = s3.groupby("2012-12-05", as_index=False).agg({"6.9": "sum"})
agg_8 = s8.groupby("2012-12-05", as_index=False).agg({"20.3333": "sum"})

agg = agg.merge(agg_6, on="2012-12-05", how="outer")
agg = agg.merge(agg_3, on="2012-12-05", how="outer")
agg = agg.merge(agg_8, on="2012-12-05", how="outer")

df = agg.merge(s4, on="2012-12-05", how="outer")
df = df.merge(s5, on="2012-12-05", how="outer")
df = df.merge(s1, on="2012-12-05", how="outer")
df = df.merge(s2, on="2012-12-05", how="outer")
df = df.merge(s9, on="2012-12-05", how="outer")
df = df.merge(s0, on="2012-12-05", how="outer")

df["301.0"] = df["301.0"].astype("Int64")
df["0.0075805085"] = df["0.0075805085"].astype(float)
df["0.0179"] = df["0.0179"].astype(float)
df["6.9"] = df["6.9"].astype(float)
df["0.17657143"] = df["0.17657143"].astype(float)
df["20.3333"] = df["20.3333"].astype(float)
df["0.016157143"] = df["0.016157143"].astype(float)
df["242.364"] = df["242.364"].astype(float)
df["0.1646"] = df["0.1646"].astype(float)
df["0.7268"] = df["0.7268"].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)