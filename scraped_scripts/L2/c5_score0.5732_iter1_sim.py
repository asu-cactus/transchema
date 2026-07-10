import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["city"], value_vars=["driver_count", "type"], var_name="variable", value_name="ride_id")
df0_unpivot = df0_unpivot[df0_unpivot["variable"] == "driver_count"].copy()
df0_unpivot["ride_id"] = pd.to_numeric(df0_unpivot["ride_id"], errors='coerce')
df0_unpivot = df0_unpivot[["city", "ride_id"]]

df1_subset = df1[["city", "ride_id"]].copy()
df1_subset["ride_id"] = pd.to_numeric(df1_subset["ride_id"], errors='coerce')

result = pd.concat([df0_unpivot, df1_subset], ignore_index=True)
result = result[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_5/target_multisource_mcts.csv", index=False)