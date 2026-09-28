import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df = df.dropna(subset=["conservation_status"])
grouped = df.groupby("conservation_status").size().reset_index(name="scientific_name")
grouped["scientific_name"] = grouped["scientific_name"].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)