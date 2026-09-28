import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_1.csv", index_col=0)

grouped0 = df0.groupby("fname").size().reset_index(name="row_count")
grouped1 = df1.groupby("fname").size().reset_index(name="row_count")

result = pd.concat([grouped0, grouped1], ignore_index=True)
result = result.groupby("fname", as_index=False)["row_count"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_86/target_multisource_mcts.csv", index=False)