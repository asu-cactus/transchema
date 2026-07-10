import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
grouped = df0.groupby("conservation_status", dropna=False).size().reset_index(name="scientific_name")
grouped = grouped[grouped["conservation_status"].notna()]
grouped["conservation_status"] = grouped["conservation_status"].astype(str)
grouped["scientific_name"] = grouped["scientific_name"].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)