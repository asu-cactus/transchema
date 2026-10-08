import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_99/training_1.csv", index_col=0)

# Join on CLUES to use both sources
df_joined = pd.merge(df0, df1, on="CLUES", how="inner")

# Group by MOTATE_V and sum count
df_target = df_joined.groupby("MOTATE_V", dropna=False, as_index=False)["count"].sum()

# Ensure correct types
df_target["MOTATE_V"] = df_target["MOTATE_V"].astype(str)
df_target["count"] = df_target["count"].astype(int)

# Write output
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length3_99/target_multisource_mcts.csv", index=False)