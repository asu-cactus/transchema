import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["TechType", "population", "state"], value_vars=["HighSpeed"], 
                       var_name="Broadband Initiative", value_name="Federal")
df0_unpivot = df0_unpivot.drop(columns=["TechType"])

df_merged = pd.merge(df0_unpivot, df1, on="state", how="inner")

result = df_merged[["Broadband Initiative", "Federal_y", "Percent", "state", "population_x"]]
result.columns = ["Broadband Initiative", "Federal", "Percent", "state", "population"]

result["Broadband Initiative"] = pd.to_numeric(result["Broadband Initiative"], errors='coerce').fillna(0).astype(int)
result["Federal"] = pd.to_numeric(result["Federal"], errors='coerce').fillna(0).astype(int)
result["Percent"] = pd.to_numeric(result["Percent"], errors='coerce').astype(float)
result["state"] = result["state"].astype(str)
result["population"] = pd.to_numeric(result["population"], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)