import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

# Join on 'state'
joined = pd.merge(df0, df1, on="state", how="inner")

# Group by 'state' and aggregate accordingly
agg = joined.groupby("state").agg({
    "Broadband Initiative": "sum",
    "Federal": "sum",
    "Percent": "mean",
    "population": "sum"
}).reset_index()

# Reorder columns to match target schema
result = agg[["Broadband Initiative", "Federal", "Percent", "state", "population"]]

# Cast types to match target schema
result["Broadband Initiative"] = result["Broadband Initiative"].astype(int)
result["Federal"] = result["Federal"].astype(int)
result["Percent"] = result["Percent"].astype(float)
result["state"] = result["state"].astype(str)
result["population"] = result["population"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)