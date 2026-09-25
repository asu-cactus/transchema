import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

# Filter out rows with missing PRODUCTLINE or SALES
df0_filtered = df0[df0["PRODUCTLINE"].notna() & df0["SALES"].notna()]

# Group by PRODUCTLINE and sum SALES
df0_grouped = df0_filtered.groupby("PRODUCTLINE", as_index=False)["SALES"].sum()

# Ensure correct types
df0_grouped["PRODUCTLINE"] = df0_grouped["PRODUCTLINE"].astype(str)
df0_grouped["SALES"] = df0_grouped["SALES"].astype(float)

df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)