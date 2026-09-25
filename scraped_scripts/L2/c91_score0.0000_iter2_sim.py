import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="calaccess_committee_id")

grouped = merged.groupby("committee_name", dropna=False, as_index=False)["amount"].sum()

grouped = grouped.rename(columns={"committee_name": "committee_name_x", "amount": "amount"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_91/target_multisource_mcts.csv", index=False)