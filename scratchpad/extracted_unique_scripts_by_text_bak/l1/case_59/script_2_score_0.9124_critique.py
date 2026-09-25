import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

# Filter out rows with null PRODUCTLINE or SALES
df0 = df0[df0["PRODUCTLINE"].notnull() & df0["SALES"].notnull()]

# Strip whitespace from PRODUCTLINE
df0["PRODUCTLINE"] = df0["PRODUCTLINE"].str.strip()

# Group by PRODUCTLINE and sum SALES
result = df0.groupby("PRODUCTLINE", dropna=False)["SALES"].sum().reset_index()

result["PRODUCTLINE"] = result["PRODUCTLINE"].astype(str)
result["SALES"] = result["SALES"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)