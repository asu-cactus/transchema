import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_76/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="city", how="inner")

pivoted = joined.pivot_table(index="city", values=["fare", "ride_id"], aggfunc="mean").reset_index()

pivoted["fare"] = pivoted["fare"].astype(float)
pivoted["ride_id"] = pivoted["ride_id"].astype(int)

pivoted[["city", "fare", "ride_id"]].to_csv("autopipeline-benchmarks/github-pipelines/length2_76/target_multisource_mcts.csv", index=False)