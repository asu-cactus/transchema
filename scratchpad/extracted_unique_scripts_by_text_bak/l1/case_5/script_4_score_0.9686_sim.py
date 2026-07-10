import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_5/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_5/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="ProvinciaID", how="inner")

result = merged[["ProvinciaID", "ProvinciaNombre", "RegionID", "ComunaID", "ComunaNombre"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_5/target_multisource_mcts.csv", index=False)