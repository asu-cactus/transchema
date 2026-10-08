import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_1.csv", index_col=0)

df_joined = pd.merge(df0, df1, on="calaccess_committee_id", how="inner", suffixes=('_0', '_1'))

df_joined = df_joined.rename(columns={"committee_name_1": "committee_name_x"})

grouped = df_joined.groupby("committee_name_x", as_index=False)["amount"].sum()

grouped["amount"] = grouped["amount"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_6/target_multisource_mcts.csv", index=False)