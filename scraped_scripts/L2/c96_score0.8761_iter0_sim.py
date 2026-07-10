import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_96/training_1.csv", index_col=0)

df0_grouped = df0.groupby("fname").size().reset_index(name="row_count")
df1_grouped = df1.groupby("fname").size().reset_index(name="row_count")

df_all = pd.concat([df0_grouped, df1_grouped], ignore_index=True)
result = df_all.groupby("fname", as_index=False)["row_count"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_96/target_multisource_mcts.csv", index=False)