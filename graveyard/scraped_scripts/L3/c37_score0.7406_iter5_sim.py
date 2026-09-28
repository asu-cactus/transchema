import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

r0 = pd.merge(s3, s1, on="County", how="outer")
r1 = pd.merge(r0, s0, on="County", how="outer")
r2 = pd.merge(r1, s2, on="County", how="outer")

melted = r2.melt(id_vars=["County"], value_vars=["r1401", "r1403"], var_name="variable", value_name="value")

pivoted = melted.pivot_table(index="County", columns="variable", values="value", aggfunc='first').reset_index()

result = pivoted[["County", "r1401", "r1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)