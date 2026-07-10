import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_76/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_76/training_1.csv", index_col=0)

joined = pd.merge(source0, source1, on="city", how="inner")

agg = joined.groupby(["city", "ride_id"], as_index=False).agg({"fare": "mean"})

agg["ride_id"] = agg["ride_id"].astype(int)
agg["city"] = agg["city"].astype(str)
agg["fare"] = agg["fare"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_76/target_multisource_mcts.csv", index=False)