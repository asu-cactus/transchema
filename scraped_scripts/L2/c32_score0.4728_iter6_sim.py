import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_1.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=["city"], value_vars=["driver_count", "type"], var_name="attribute", value_name="value")

df_joined = pd.merge(df0, df1_unpivot, on="city", how="inner")

result = df_joined[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv", index=False)