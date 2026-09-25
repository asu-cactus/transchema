import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_0.csv", index_col=0)

grouped = df0.groupby("committee_name", as_index=False)["amount"].sum()
grouped = grouped.rename(columns={"committee_name": "committee_name_x", "amount": "amount"})
grouped["amount"] = grouped["amount"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_91/target_multisource_mcts.csv", index=False)