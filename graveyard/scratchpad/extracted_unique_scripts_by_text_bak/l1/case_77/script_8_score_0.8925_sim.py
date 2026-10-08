import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
result = df0.groupby("fac_type", as_index=False)["capacity"].sum()
result["fac_type"] = result["fac_type"].astype(str)
result["capacity"] = result["capacity"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)