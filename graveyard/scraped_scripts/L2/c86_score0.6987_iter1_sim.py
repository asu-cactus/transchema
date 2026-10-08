import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_1.csv", index_col=0)

df0_agg = df0.groupby("fname").size().reset_index(name="row_count")
df1_agg = df1.groupby("fname").size().reset_index(name="row_count")

df = pd.concat([df0_agg, df1_agg], ignore_index=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_86/target_multisource_mcts.csv", index=False)