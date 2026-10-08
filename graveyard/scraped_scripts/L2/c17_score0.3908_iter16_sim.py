import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["TechType", "population", "state"], value_vars=["HighSpeed"], 
                       var_name="Broadband Initiative", value_name="Federal")
df0_unpivot["Broadband Initiative"] = df0_unpivot["Broadband Initiative"].map({"HighSpeed": 5769942})

df0_grouped = df0_unpivot.groupby(["Broadband Initiative", "state"], as_index=False).agg({
    "Federal": "sum",
    "population": "sum"
})

df1["Broadband Initiative"] = df1["Broadband Initiative"].astype(int)
df1["Federal"] = df1["Federal"].astype(int)
df1["Percent"] = df1["Percent"].astype(float)
df1["population"] = df1.get("population", pd.NA)

df0_grouped["Percent"] = 0.0
df0_grouped = df0_grouped[["Broadband Initiative", "Federal", "Percent", "state", "population"]]

df_final = pd.concat([df0_grouped, df1], ignore_index=True, sort=False)

df_final = df_final.astype({
    "Broadband Initiative": "int64",
    "Federal": "int64",
    "Percent": "float64",
    "state": "string",
    "population": "Int64"
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)