import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

agg = df1.groupby("city").agg(a=("driver_count", "mean"), b=("type", "count")).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)