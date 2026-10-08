import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"type": "fare"})
df0_renamed["fare"] = pd.to_numeric(df0_renamed["fare"], errors='coerce')
df0_renamed["ride_id"] = pd.NA
df0_renamed["fare"] = df0_renamed["fare"].fillna(0)

df1_selected = df1[["city", "fare", "ride_id"]].copy()
df1_selected["driver_count"] = pd.NA

df0_final = df0_renamed[["city", "driver_count", "fare", "ride_id"]]
df1_final = df1_selected[["city", "driver_count", "fare", "ride_id"]]

df_final = pd.concat([df0_final, df1_final], ignore_index=True)

df_final["city"] = df_final["city"].astype(str)
df_final["driver_count"] = pd.to_numeric(df_final["driver_count"], errors='coerce').astype("Int64")
df_final["fare"] = pd.to_numeric(df_final["fare"], errors='coerce').astype(float)
df_final["ride_id"] = pd.to_numeric(df_final["ride_id"], errors='coerce').astype(float)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)