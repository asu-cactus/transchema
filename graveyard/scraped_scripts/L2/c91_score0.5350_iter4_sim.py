import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="calaccess_committee_id", how="inner")

grouped = merged.groupby("committee_name_y", dropna=False, as_index=False)["amount"].sum()

grouped = grouped.rename(columns={"committee_name_y": "committee_name_x", "amount": "amount"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_91/target_multisource_mcts.csv", index=False)