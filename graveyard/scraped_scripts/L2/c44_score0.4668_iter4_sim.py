import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

pivoted = merged.pivot_table(index=["city", "fare", "ride_id"], columns="type", values="driver_count", aggfunc='first').reset_index()

result = pivoted[["city", "fare", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_44/target_multisource_mcts.csv", index=False)