import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_1.csv", index_col=0)

agg_df0 = df0.groupby("fname").size().reset_index(name="row_count")

agg_df0.to_csv("autopipeline-benchmarks/github-pipelines/length2_86/target_multisource_mcts.csv", index=False)