import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_0.csv", index_col=0)

agg = df0.groupby("committee_name").agg(amount_min=("amount", "min"), amount_max=("amount", "max")).reset_index()

agg["amount"] = agg[["amount_min", "amount_max"]].max(axis=1)

result = agg.rename(columns={"committee_name": "committee_name_x"})[["committee_name_x", "amount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_91/target_multisource_mcts.csv", index=False)