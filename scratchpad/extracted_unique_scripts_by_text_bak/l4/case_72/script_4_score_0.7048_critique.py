import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

agg_df0 = df0.groupby("city").agg(a=("fare", "mean")).reset_index()
agg_df1 = df1.groupby("city").agg(b=("driver_count", "sum")).reset_index()

result = pd.merge(agg_df0, agg_df1, on="city", how="inner")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)