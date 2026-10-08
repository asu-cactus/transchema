import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

join_31 = pd.merge(source3, source1, on="County", how="outer")
join_310 = pd.merge(join_31, source0, on="County", how="outer")
join_all = pd.merge(join_310, source2, on="County", how="outer")

result = join_all.groupby(["County", "r1401", "r1403"], dropna=False, as_index=False).size()

result = result[["County", "r1401", "r1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)