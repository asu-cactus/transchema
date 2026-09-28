import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

# Ensure correct types for joining and aggregation
df1["Broadband Initiative"] = df1["Broadband Initiative"].astype(int)
df1["Federal"] = df1["Federal"].astype(int)
df1["Percent"] = df1["Percent"].astype(float)
df0["population"] = df0["population"].astype(int)
df0["state"] = df0["state"].astype(str)
df1["state"] = df1["state"].astype(str)

# Join on 'state'
df_joined = pd.merge(df1, df0[["population", "state"]], on="state", how="inner")

# Group by 'Broadband Initiative' and 'state'
df_grouped = df_joined.groupby(["Broadband Initiative", "state"], as_index=False).agg({
    "Federal": "sum",
    "Percent": "mean",
    "population": "sum"
})

# Reorder columns to match target schema
df_grouped = df_grouped[["Broadband Initiative", "Federal", "Percent", "state", "population"]]

# Set correct dtypes matching target schema
df_grouped = df_grouped.astype({
    "Broadband Initiative": "int64",
    "Federal": "int64",
    "Percent": "float64",
    "state": "string",
    "population": "int64"
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)