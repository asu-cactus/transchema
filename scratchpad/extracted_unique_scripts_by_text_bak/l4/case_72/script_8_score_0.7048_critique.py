import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

joined = pd.merge(source0, source1, on="city", how="inner")

agg = joined.groupby("city").agg(a=("fare", "mean"), b=("ride_id", "count")).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)