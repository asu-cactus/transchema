import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"type": "fare", "driver_count": "driver_count", "city": "city"})
df0_renamed["fare"] = pd.to_numeric(df0_renamed["fare"], errors='coerce')
df0_renamed["ride_id"] = pd.NA
df0_renamed["driver_count"] = pd.to_numeric(df0_renamed["driver_count"], errors='coerce').astype("Int64")

df1_selected = df1[["city", "fare", "ride_id"]].copy()
df1_selected["driver_count"] = pd.NA
df1_selected["driver_count"] = df1_selected["driver_count"].astype("Int64")

df_union = pd.concat([df0_renamed[["city", "fare", "ride_id", "driver_count"]], df1_selected[["city", "fare", "ride_id", "driver_count"]]], ignore_index=True)

df_union["city"] = df_union["city"].astype(str)
df_union["fare"] = pd.to_numeric(df_union["fare"], errors='coerce')
df_union["ride_id"] = pd.to_numeric(df_union["ride_id"], errors='coerce')
df_union["driver_count"] = df_union["driver_count"].astype("Int64")

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)