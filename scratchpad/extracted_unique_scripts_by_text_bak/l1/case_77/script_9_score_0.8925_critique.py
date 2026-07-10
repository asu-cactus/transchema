import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df0["fac_type"] = df0["fac_type"].str.strip()
result = df0.groupby("fac_type", as_index=False)["capacity"].sum()
result["capacity"] = result["capacity"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)