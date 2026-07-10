import pandas as pd

Source3_36_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
Source3_36_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
Source3_36_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)

join_01 = pd.merge(Source3_36_1, Source3_36_0, on="County", how="outer")
join_result = pd.merge(join_01, Source3_36_2, on="County", how="outer")

Target3_36 = join_result[["County", "m1401", "m1403"]]

Target3_36.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv")