import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

grouped = df.groupby("fac_type", as_index=False)["capacity"].sum()
grouped["capacity"] = grouped["capacity"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)