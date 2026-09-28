import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv", index_col=0)

grouped = df1.groupby("city", as_index=False)["ride_id"].first()

result = grouped[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv", index=False)