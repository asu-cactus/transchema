import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

joined = pd.merge(source0, source3, left_on="COD_OFICIPAL", right_on="COD_OFICI")

result = joined.groupby("des_territ", dropna=False).size().reset_index(name="count").drop(columns="count")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)