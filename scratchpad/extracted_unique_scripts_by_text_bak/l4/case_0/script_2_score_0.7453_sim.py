import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

result = src3.groupby("des_territ", dropna=False).size().reset_index(name="count")
output = result[["des_territ"]]

output.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)