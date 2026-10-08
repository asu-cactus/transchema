import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)  # County, r1403
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)  # County, r1402 (not needed in output)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)  # County only
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)  # County, r1401

# Join s3 and s0 on County
r = pd.merge(s3, s0, on="County", how="outer")

# Join with s2 (dimension table with all counties)
r = pd.merge(r, s2, on="County", how="outer")

# Join with s1 (has r1402, not needed in output but must be used)
r = pd.merge(r, s1, on="County", how="outer")

# Select only columns needed for target
result = r[["County", "r1401", "r1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)