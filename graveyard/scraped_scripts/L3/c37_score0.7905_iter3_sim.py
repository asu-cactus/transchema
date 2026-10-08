import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

df = source3.merge(source0, on="County", how="inner").merge(source1, on="County", how="inner")

result = df.groupby(["County", "r1401", "r1403"], as_index=False).size()

result = result.drop(columns="size")

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)