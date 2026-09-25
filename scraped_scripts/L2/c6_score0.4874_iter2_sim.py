import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_1.csv", index_col=0)

agg = df2.groupby("committee_name", dropna=False, as_index=False)["amount"].sum()
agg = agg.rename(columns={"committee_name": "committee_name_x", "amount": "amount"})
agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_6/target_multisource_mcts.csv", index=False)