import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["city", "date"], value_vars=["fare", "ride_id"], var_name="var", value_name="val")

df0_unpivot["a"] = df0_unpivot.apply(lambda row: float(row["val"]) if row["var"] == "fare" else None, axis=1)
df0_unpivot["b"] = df0_unpivot.apply(lambda row: int(row["val"]) if row["var"] == "ride_id" else None, axis=1)

df0_agg = df0_unpivot.groupby(["city"]).agg({"a": "mean", "b": "sum"}).reset_index()

df1_agg = df1.groupby("city").agg({"driver_count": "sum"}).reset_index()

df_joined = pd.merge(df0_agg, df1_agg, on="city", how="inner")

df_joined = df_joined.rename(columns={"driver_count": "b"})

df_result = df_joined[["city", "a", "b"]]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)