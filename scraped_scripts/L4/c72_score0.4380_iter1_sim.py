import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=["city", "type"], value_vars=["driver_count"], var_name="variable", value_name="b")
df1_unpivot = df1_unpivot.drop(columns=["variable", "type"])

df_merged = pd.merge(df0, df1_unpivot, on="city", how="inner")

result = df_merged[["city", "fare", "b"]].rename(columns={"fare": "a"})
result["a"] = result["a"].astype(float)
result["b"] = result["b"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)