import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)
df0_filtered = df0[df0["Major_category"].notnull() & df0["Median"].notnull()]
result = df0_filtered[["Major_category", "Median"]].copy()
result["Median"] = result["Median"].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)