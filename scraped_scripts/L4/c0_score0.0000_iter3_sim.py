import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

j1 = pd.merge(s1, s2, on="COD_IDCONTRA", how="inner")
j2 = pd.merge(j1, s0, on="COD_PERSONA", how="inner")
j3 = pd.merge(j2, s3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

result = j3.groupby("des_territ", as_index=False).size().rename(columns={"size": "count"})
result = result[["des_territ"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)